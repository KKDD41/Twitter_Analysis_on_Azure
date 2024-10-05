CREATE TABLE tweets (
	id text,
	created_at text,
	"text" text
)

CREATE TABLE mentions (
	username text,
	tweet_id text
)

CREATE TABLE total_mentions (
    username text,
    "count" int
)

CREATE TABLE tweets_by_date (
    "date" date,
    "count" int
)