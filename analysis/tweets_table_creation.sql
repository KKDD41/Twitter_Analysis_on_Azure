CREATE TABLE tweets (
	id text,
	created_at text,
	"text" text,
	week_day int,
	text_length int
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
    "count" int,
    total_tweets_length int
)