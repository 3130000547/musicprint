
import hashlib
import time
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import (generate_binary_structure,
                                      iterate_structure, binary_erosion)
from pydub import AudioSegment
from pydub.utils import audioop
from hashlib import sha1
from operator import itemgetter

#根据音乐文件名生成哈希字符串
def unique_hash(filepath, blocksize=2**20):

    s = sha1()
    with open(filepath , "rb") as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            s.update(buf)
    return s.hexdigest().upper()

#读取mp3文件，返回通道，取样数，文件名哈希字符串
def read(filename):
    
    audiofile = AudioSegment.from_mp3(filename)
    data = np.fromstring(audiofile._data, np.int16)
    channels = []
    for chn in range(audiofile.channels):
        channels.append(data[chn::audiofile.channels])
    fs = audiofile.frame_rate

    return channels, audiofile.frame_rate, unique_hash(filename)

IDX_FREQ_I = 0#频率下标
IDX_TIME_J = 1#时间下标
DEFAULT_FS = 44100#采样率
DEFAULT_WINDOW_SIZE = 4096#FFT窗口大小
DEFAULT_OVERLAP_RATIO = 0.5#重叠率
DEFAULT_FAN_VALUE = 10#每个点配对数
DEFAULT_AMP_MIN = 20#峰值点最低最低振幅
PEAK_NEIGHBORHOOD_SIZE = 20#峰值点邻域范围
MIN_HASH_TIME_DELTA = 2
MAX_HASH_TIME_DELTA = 200
PEAK_SORT = True#临时为峰值点排序
FINGERPRINT_REDUCTION = 20

def fingerprint(channel_samples, Fs=DEFAULT_FS,
                wsize=DEFAULT_WINDOW_SIZE,
                wratio=DEFAULT_OVERLAP_RATIO,
                fan_value=DEFAULT_FAN_VALUE,
                amp_min=DEFAULT_AMP_MIN):
    
    arr2D = mlab.specgram(
            channel_samples,
            NFFT=wsize,
            Fs=Fs,
            window=mlab.window_hanning,
            noverlap=int(wsize * wratio))[0]

    # apply log transform since specgram() returns linear array
    arr2D = 10 * np.log10(arr2D)
    arr2D[arr2D == -np.inf] = 0  # replace infs with zeros

    # find local maxima
    hash_list= get_2D_peaks(arr2D, plot=True, amp_min=amp_min)

    return hash_list
    # return hashes
    #phash = generate_hashes(peaks = local_maxima, fan_value=fan_value)
    #return phash

def get_2D_peaks(arr2D, plot=False, amp_min=DEFAULT_AMP_MIN):
 
    struct = generate_binary_structure(2, 1)
    neighborhood = iterate_structure(struct, PEAK_NEIGHBORHOOD_SIZE)

    # 寻找局部峰值点
    local_max = maximum_filter(arr2D, footprint=neighborhood) == arr2D
    background = (arr2D == 0)
    eroded_background = binary_erosion(background, structure=neighborhood, border_value=1)

    # Boolean mask of arr2D with True at peaks
    detected_peaks = local_max - eroded_background

    # 提取峰值点
    amps = arr2D[detected_peaks]
    j, i = np.where(detected_peaks)

    # filter peaks
    amps = amps.flatten()
    peaks = list(zip(i, j, amps))
    peaks_filtered = [x for x in peaks if x[2] > amp_min]  # freq, time, amp

    # get indices for frequency and time
    frequency_idx = [x[1] for x in peaks_filtered]
    time_idx = [x[0] for x in peaks_filtered]

    if plot:
        # scatter of the peaks
        fig, ax = plt.subplots()
        ax.imshow(arr2D)
        ax.scatter(time_idx, frequency_idx)#在图上绘制散点
        ax.set_xlabel('Time')
        ax.set_ylabel('Frequency')
        ax.set_title("Spectrogram")
        plt.gca().invert_yaxis()
        plt.show()

    peaklist = list(zip(frequency_idx, time_idx))
    h = []

    for i in range(len(peaklist)):
        for j in range(1, DEFAULT_FAN_VALUE):
            if (i + j) < len(peaklist):
                
                freq1 = peaklist[i][IDX_FREQ_I]
                freq2 = peaklist[i + j][IDX_FREQ_I]
                t1 = peaklist[i][IDX_TIME_J]
                t2 = peaklist[i + j][IDX_TIME_J]
                t_delta = t2 - t1

                if t_delta >= MIN_HASH_TIME_DELTA and t_delta <= MAX_HASH_TIME_DELTA:
                    stmp = "%s|%s|%s" % (str(freq1), str(freq2), str(t_delta))
                    h.append((hashlib.sha1(stmp.encode('utf-8')).hexdigest().upper(),t1))

    return h

def getsongprint(songname):
    channels, fs, fhash = read(songname)
    #只读取第一个声道
    phash = fingerprint(channel_samples = channels[0], Fs=fs)

    return songname, fhash, phash