from bot_logging import logger

from time import sleep

import praw
from prawcore.exceptions import (RequestException, ResponseException, ServerError)

from constants import *
from database.database import Session, engine
import database.crud as crud
import database.models as models

models.Base.metadata.create_all(bind=engine)


def ingest():
	r = praw.Reddit(PRAW_USER)
	r.validate_on_submit = True
	sub = r.subreddit(SUBREDDIT)
	iface = crud.Interface(sub=sub)
	session = Session()

	postStream = sub.stream.submissions(pause_after=-1)
	commentStream = sub.stream.comments(pause_after=-1)
	
	for post in sub.new(limit=None): iface.upsert_post(session, post)
	for comment in sub.comments(limit=None): iface.upsert_comment(session, comment)
 
	logger.log("EPHEMERAL","Starting live streams")

	while True:
		try:
			try:
				for item in postStream:
					if item is not None: iface.upsert_post(session, item)
					else: break
			except KeyboardInterrupt:
				logger.info('Keyboard interrupt detected. Goodbye!')
				session.close()
				exit()
			except:
				postStream = sub.stream.submissions(pause_after=-1)
				logger.warning("rebuilt post stream")
				for item in postStream:
					if item is not None: iface.upsert_post(session, item)
					else: break
 
			try:
				for item in commentStream:
					if item is not None: iface.upsert_comment(session, item)
					else: break
			except KeyboardInterrupt:
				logger.info('Keyboard interrupt detected. Goodbye!')
				session.close()
				exit()
			except:
				commentStream = sub.stream.comments(pause_after=-1)
				logger.warning("rebuilt edit stream")
				for item in commentStream:
					if item is not None: iface.upsert_comment(session, item)
					else: break


				
		except ServerError as e:
			logger.error(f'Caught praw ServerError: {str(e)}')
			session.rollback()
			sleep(60)
			continue
		except RequestException as e:
			logger.error(f'Caught praw RequestException: {str(e)}')
			session.rollback()
			sleep(60)
			continue
		except ResponseException as e:
			logger.error(f'Caught praw ResponseException: {str(e)}')
			session.rollback()
			sleep(60)
			continue
		except KeyboardInterrupt:
			logger.info('Keyboard interrupt detected. Goodbye!')
			session.close()
			exit()

 
if __name__ == '__main__': ingest()