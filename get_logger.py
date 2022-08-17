import logging


def get_logger(fn='mmcs_news', logger_name='mmcs_news'):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler(fn)
    formatter = logging.Formatter('%(asctime)s - %(name)s.%(levelname)s: %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger
