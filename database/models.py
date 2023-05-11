from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
	__tablename__ = 'users'

	name        = Column(String(20), primary_key=True, unique=True)
	deleted     = Column(INTEGER(1)) 

	def __repr__(self):
		return f"<User(username='{self.name}')>"


class Post(Base):
	__tablename__ = 'posts'

	id          = Column(String(20), primary_key=True, unique=True)
	author      = Column(ForeignKey('users.name'), nullable=False, index=True)
	created_utc = Column(INTEGER(11), nullable=False)
	edited      = Column(INTEGER(11), nullable=False)
	over_18     = Column(INTEGER(1), nullable=False)
	score       = Column(INTEGER(5), nullable=False)
	selftext    = Column(Text(160000), nullable=False)
	spoiler     = Column(INTEGER(1), nullable=False)
	subreddit   = Column(String(20))
	title       = Column(String(1200), nullable=False)
	url         = Column(String(1200), nullable=False)
 
	user_obj     = relationship('User')

	def __repr__(self):
		return f"<Post(post_id='{self.id}', author='{self.author}', created_utc='{self.created_utc}')>"

class Comment(Base):
	__tablename__ = "comments"
  
	id             = Column(String(20), primary_key=True, unique=True)
	author         = Column(ForeignKey('users.name'), nullable=False, index=True)
	body           = Column(Text(40000), nullable=False)
	created_utc    = Column(INTEGER(11), nullable=False)
	edited         = Column(INTEGER(1), nullable=False)
	is_submitter   = Column(INTEGER(1), nullable=False)
	link_id        = Column(ForeignKey('posts.id'), nullable=False, index=True)
	parent_id      = Column(String(20))
	score          = Column(INTEGER(5), nullable=False)
	subreddit      = Column(String(20))
 
	link_obj       = relationship('Post')

	def __repr__(self):
		return f"<Comment(id='{self.id}', user='{self.author}', created_utc='{self.created_utc}')>"