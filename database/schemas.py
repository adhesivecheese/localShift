from pydantic import BaseModel
from typing import List, Union

class OrmBase(BaseModel):
		def _iter(self, to_dict: bool = False, *args, **kwargs):
				for dict_key, v in super()._iter(to_dict, *args, **kwargs):
						if to_dict and self.__fields__[dict_key].field_info.extra.get('flatten', False):
								assert isinstance(v, dict)
								yield from v.items()
						else:
								yield dict_key, v
		class Config:
			orm_mode = True
			allow_population_by_field_name = True


class Post(OrmBase):
	id: str
	author: str
	created_utc: int
	edited: int
	over_18: bool
	score: int
	selftext: str
	spoiler: bool
	subreddit: str
	title: str
	url: str


class Comment(OrmBase):
	id: str
	author: str
	body: str
	created_utc: int
	edited: int
	is_submitter: bool
	link_id: str
	parent_id: Union[str, None]
	score: int
	subreddit: str


class User(OrmBase):
	username: str
	deleted: int


class User_History(OrmBase):
	username: str
	deleted: int
	posts: List[Post]
	comments: List[Comment]