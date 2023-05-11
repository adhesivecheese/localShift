from bot_logging import logger

from sqlalchemy.orm import Session
from prawcore.exceptions import NotFound

from . import models


class Interface():
	def __init__(self, sub=None):
		self.sub = sub
		self.r = sub._reddit

	@logger.catch
	def upsert_user(self, db: Session, user, updates={}, on_conflict="UPDATE") -> models.User:
		username = self.__user_exists(user)
		db_item = self.read_user(db, username)
		if db_item is None: return self._create_user(db, user)
		if on_conflict== "UPDATE" and updates != {}:
			user = self._update_user(db, user, updates)
			return user
		else: return db_item

	@logger.catch
	def read_user(self, db: Session, username: str) -> models.User:
		user = db.query(models.User).filter(models.User.name == username).first()
		if user is None: return None
		else: return user

	@logger.catch
	def _create_user(self, db: Session, user) -> models.User:
		name = self.__user_exists(user)
		deleted = None
		if name != "[deleted]":
			try:
				self.r.request(method='get', path=f'/user/{user}/about')['data']['is_suspended']
				deleted= -1
			except KeyError:
				deleted = None
			except NotFound:
				deleted = 1
		else:
			deleted_user = self.read_user(db, name)
			if deleted_user is not None: return deleted_user

		db_user = models.User(name=name, deleted=deleted)
		return self.__add_item(db, db_user)

	@logger.catch
	def _update_user(self, db: Session, user, updates: dict = {}) -> models.User:
		username = self.__user_exists(user)
		db_item = self.read_user(db, username)
		if updates == {}: return db_item
		user = self.__update_db_by_dict(updates, db_item)
		self.__add_item(db, user)
		return user


	@logger.catch
	def upsert_post(self, db: Session, post, on_conflict="IGNORE", updates: dict = {}) -> models.Post:
		db_item = self.read_post(db, post.id)
		if db_item is None:
			logger.debug(f"Inserting post '{post.id}'")
			return self._create_post(db, post)
		if on_conflict == "UPDATE":
			logger.debug(f"Updating post '{post.id}'")
			return self._update_post(db, post, updates)
		else:
			logger.debug(f"Post '{post.id}' already exists in the database, ignoring")
			return db_item

	@logger.catch
	def read_post(self, db: Session, id: str) -> models.Post:
		post = db.query(models.Post).filter(models.Post.id == id).first()
		if post is None:
			logger.debug(f"Attempted to read non-existant post '{id}', returning None")
			return None
		else:
			logger.debug(f"Returning existing post '{id}'")
			return post

	@logger.catch
	def _create_post(self, db: Session, post) -> models.Post:
		db_user = self.upsert_user(db, post.author)
		db_post = models.Post(
			  id=post.id
		    , author=db_user.name
			, created_utc=int(post.created_utc)
			, edited = post.edited
			, over_18 = post.over_18
			, score = post.score
			, selftext = post.selftext
			, spoiler = post.spoiler
			, subreddit = post.subreddit.display_name
			, title=post.title
			, url=post.url
		)
		return self.__add_item(db, db_post)

	@logger.catch
	def _update_post(self, db: Session, post, updates: dict = {}) -> models.Post:
		db_item = self.read_post(db, post.id)
		if updates == {}:
			logger.log("EPHEMERAL",f"Empty updated called for post '{post.id}', ignoring")
			return db_item
		db_post = self.__update_db_by_dict(updates, db_item)
		return self.__add_item(db, db_post)


	@logger.catch
	def upsert_comment(self, db: Session, comment, on_conflict="IGNORE", updates: dict = {}) -> models.Comment:
		db_item = self.read_comment(db, comment.id)
		if db_item is None:
			logger.debug(f"Inserting comment '{comment.id}'")
			return self._create_comment(db, comment)
		if on_conflict == "UPDATE":
			logger.debug(f"Updating comment '{comment.id}'")
			return self._update_comment(db, comment, updates)
		else:
			logger.debug(f"comment '{comment.id}' already exists in the database, ignoring")
			return db_item

	@logger.catch
	def read_comment(self, db: Session, id: str) -> models.Comment:
		post = db.query(models.Comment).filter(models.Comment.id == id).first()
		if post is None:
			logger.debug(f"Attempted to read non-existant comment '{id}', returning None")
			return None
		else:
			logger.debug(f"Returning existing comment '{id}'")
			return post

	@logger.catch
	def _create_comment(self, db: Session, comment) -> models.Comment:
		user = self.upsert_user(db, comment.author)
		self.upsert_post(db, comment.submission)
		db_comment = models.Comment(
			  id             = comment.id
			, author         = user.name
			, body           = comment.body
			, created_utc    = int(comment.created_utc)
			, edited         = comment.edited
			, is_submitter   = comment.is_submitter
			, link_id        = comment.link_id[3:]
			, score          = comment.score
			, subreddit      = comment.subreddit.display_name
		)
		if comment.parent_id.startswith("t1_"):
			db_comment.parent_id = comment.parent_id[3:]
		return self.__add_item(db, db_comment)

	@logger.catch
	def _update_comment(self, db: Session, comment, updates: dict = {}) -> models.Comment:
		db_item = self.read_comment(db, comment.id)
		if updates == {}:
			logger.log("EPHEMERAL",f"Empty updated called for comment '{comment.id}', ignoring")
			return db_item
		db_comment = self.__update_db_by_dict(updates, db_item)
		return self.__add_item(db, db_comment)

	@logger.catch
	def __add_item(self, db: Session, item):
		db.add(item)
		db.commit()
		db.refresh(item)
		logger.log("EPHEMERAL",f"{item} committed to Database")
		return item

	@logger.catch
	def __user_exists(self, user):
		try: name = user.name
		except: name = "[deleted]"
		return name

	@logger.catch
	def __update_db_by_dict(self, updates, db_item):
		for key, value in updates.items():
			if key in db_item.__dict__:
				setattr(db_item, key, value)
				logger.log("EPHEMERAL",f"set '{key}'='{value}' for {db_item}")
		return db_item

class ReadOnlyInterface:
	@logger.catch
	def read_user(self, db: Session, username: str) -> models.User:
		user = db.query(models.User).filter(models.User.name == username).first()
		if user is None: return None
		else: return user
  
	@logger.catch
	def read_post(self, db: Session, id: str) -> models.Post:
		post = db.query(models.Post).filter(models.Post.id == id).first()
		if post is None:
			logger.debug(f"Attempted to read non-existant post '{id}', returning None")
			return None
		else:
			logger.debug(f"Returning existing post '{id}'")
			return post

	@logger.catch
	def read_comment(self, db: Session, id: str) -> models.Comment:
		post = db.query(models.Comment).filter(models.Comment.id == id).first()
		if post is None:
			logger.debug(f"Attempted to read non-existant comment '{id}', returning None")
			return None
		else:
			logger.debug(f"Returning existing comment '{id}'")
			return post
