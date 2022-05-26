import coloredlogs
import logging
import os
from typing import Optional

_logger = logging.getLogger().getChild(__name__)


def setup_logging(verbose: Optional[int] = None,
                  quiet: Optional[int] = None) -> None:
  verbose = 0 if verbose is None else verbose
  quiet = 0 if quiet is None else quiet
  logging_level = (quiet - verbose) * 10 + logging.INFO
  logging_level = max(logging.DEBUG, min(logging.CRITICAL, logging_level))

  coloredlogs.install(
      level=logging_level,
      fmt='[%(levelname)s %(name)s:%(lineno)d] %(message)s',
      datefmt='%m%d %H:%M:%S.%f',
  )

  # filename = os.path.join(log_dir, basename)
  handler = logging.FileHandler('rapidstream.log', encoding='utf-8')
  handler.setFormatter(
      logging.Formatter(
          fmt=('[%(levelname)s '
               '%(name)s:%(lineno)d] %(message)s'),
          datefmt='%m%d %H:%M:%S',
      ))
  handler.setLevel(logging.DEBUG)
  logging.getLogger().addHandler(handler)

  _logger.info('logging level set to %s', logging.getLevelName(logging_level))
