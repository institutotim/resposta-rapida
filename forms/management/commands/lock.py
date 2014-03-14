import errno, os


def acquire_lock(lock_path):
    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_RDWR)
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise
        return False
    else:
        return fd, lock_path


def release_lock(lock):
    if isinstance(lock, tuple):
        os.close(lock[0])
        os.unlink(lock[1])