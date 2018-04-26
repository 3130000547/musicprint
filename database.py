import pymysql
from pymysql.cursors import DictCursor
import genprint

conn = pymysql.connect(host = 'localhost', port = 3306, user = 'root', password = '54669592', db = "fingerprint")
cur=conn.cursor()

FIELD_FILE_SHA1 = 'file_sha1'
FIELD_SONG_ID = 'song_id'
FIELD_SONGNAME = 'song_name'
FIELD_OFFSET = 'offset'
FIELD_HASH = 'hash'

# tables
FINGERPRINTS_TABLENAME = "fingerprints"
SONGS_TABLENAME = "songs"

# creates
CREATE_FINGERPRINTS_TABLE = """
    CREATE TABLE IF NOT EXISTS `%s` (
         `%s` char(10) not null,
         `%s` mediumint unsigned not null,
         `%s` int unsigned not null,
     INDEX (%s),
     UNIQUE KEY `unique_constraint` (%s, %s, %s),
     FOREIGN KEY (%s) REFERENCES %s(%s) ON DELETE CASCADE
) ENGINE=INNODB;""" % (
    FINGERPRINTS_TABLENAME, FIELD_HASH,
    FIELD_SONG_ID, FIELD_OFFSET, FIELD_HASH,
    FIELD_SONG_ID, FIELD_OFFSET, FIELD_HASH,
    FIELD_SONG_ID, SONGS_TABLENAME, FIELD_SONG_ID
)
CREATE_SONGS_TABLE = """
    CREATE TABLE IF NOT EXISTS `%s` (
        `%s` mediumint unsigned not null auto_increment,
        `%s` varchar(250) not null,
        `%s` binary(20) not null,
    PRIMARY KEY (`%s`),
    UNIQUE KEY `%s` (`%s`)
) ENGINE=INNODB;""" % (
    SONGS_TABLENAME, FIELD_SONG_ID, FIELD_SONGNAME, 
    FIELD_FILE_SHA1,
    FIELD_SONG_ID, FIELD_SONG_ID, FIELD_SONG_ID,
)
# inserts (ignores duplicates)
INSERT_FINGERPRINT = """
    INSERT IGNORE INTO %s (%s, %s) values
        (UNHEX(%%s), %%s);
""" % (FINGERPRINTS_TABLENAME, FIELD_HASH, FIELD_SONG_ID)

INSERT_SONG = "INSERT INTO %s (%s, %s) values (%%s, UNHEX(%%s));" % (
    SONGS_TABLENAME, FIELD_SONGNAME, FIELD_FILE_SHA1)


def create():
    
    cur.execute(CREATE_SONGS_TABLE)
    cur.execute(CREATE_FINGERPRINTS_TABLE)

def insert(songname):

    name, songhash, printhash = genprint.getsongprint(songname)
    cur.execute(INSERT_SONG, (name, songhash))
    conn.commit()
    sid = cur.lastrowid

    for h in range(len(offset)):
        cur.execute("INSERT INTO fingerprints(hash, song_id, offset) VALUES ('%s', %d, %d);" % (str(printhash[h])[-10:], sid, int(printhash[h][1])))
    conn.commit()

    return sid
