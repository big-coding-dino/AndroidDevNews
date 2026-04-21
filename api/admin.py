import os

from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
    f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
)

db = SQLAlchemy()
db.init_app(app)


# ── Models that mirror schema.sql ──────────────────────────────────────────

class Feed(db.Model):
    __tablename__ = "feeds"
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    feed_url = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())


class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)


class Resource(db.Model):
    __tablename__ = "resources"
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey("feeds.id"))
    url = db.Column(db.Text, unique=True, nullable=False)
    title = db.Column(db.Text)
    resource_type = db.Column(db.Text, default="article")
    embedding = db.Column(db.Text)  # vector stored as text in SQLA; actual column is USER-DEFINED type
    published_at = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=db.func.now())
    summary = db.Column(db.Text)
    background = db.Column(db.Text)
    tldr = db.Column(db.Text)

    source = db.relationship("Feed", backref="resources")
    tags = db.relationship(
        "Tag",
        secondary="resource_tags",
        back_populates="resources",
    )


# association table for Resource <-> Tag
resource_tags = db.Table(
    "resource_tags",
    db.Column("resource_id", db.Integer, db.ForeignKey("resources.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
)


Tag.resources = db.relationship(
    "Resource",
    secondary="resource_tags",
    back_populates="tags",
)


class Article(db.Model):
    __tablename__ = "articles"
    resource_id = db.Column(db.Integer, db.ForeignKey("resources.id"), primary_key=True)
    clean_content = db.Column(db.Text)
    readability_content = db.Column(db.Text)
    fetch_error = db.Column(db.Text)
    scraped_date = db.Column(db.Date)
    clean_content_error = db.Column(db.Text)
    readability_error = db.Column(db.Text)

    resource = db.relationship("Resource", backref=db.backref("article", uselist=False))


class ArticleView(ModelView):
    column_list = ("resource_id", "clean_content", "readability_content",
                   "fetch_error", "scraped_date", "clean_content_error", "readability_error")


class PodcastEpisodeView(ModelView):
    column_list = ("resource_id", "episode_number", "duration_seconds", "audio_url", "diarization")


class PodcastEpisode(db.Model):
    __tablename__ = "podcast_episodes"
    resource_id = db.Column(db.Integer, db.ForeignKey("resources.id"), primary_key=True)
    episode_number = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)
    audio_url = db.Column(db.Text)
    diarization = db.Column(db.Text)  # no transcript column in DB

    resource = db.relationship("Resource", backref=db.backref("podcast_episode", uselist=False))


class NewsletterIssue(db.Model):
    __tablename__ = "newsletter_issues"
    id = db.Column(db.Integer, primary_key=True)
    feed_id = db.Column(db.Integer, db.ForeignKey("feeds.id"), nullable=False)
    issue_number = db.Column(db.Integer, nullable=False)
    published_at = db.Column(db.Date)
    __table_args__ = (db.UniqueConstraint("feed_id", "issue_number"),)

    feed = db.relationship("Feed", backref="newsletter_issues")


class NewsletterIssueResource(db.Model):
    __tablename__ = "newsletter_issue_resources"
    issue_id = db.Column(db.Integer, db.ForeignKey("newsletter_issues.id"), primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey("resources.id"), primary_key=True)


class Digest(db.Model):
    __tablename__ = "digests"
    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id"), nullable=False)
    period = db.Column(db.Text, nullable=False)
    frequency = db.Column(db.Text, default="monthly")
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    __table_args__ = (db.UniqueConstraint("tag_id", "period", "frequency"),)

    tag = db.relationship("Tag", backref="digests")


class DigestResource(db.Model):
    __tablename__ = "digest_resources"
    digest_id = db.Column(db.Integer, db.ForeignKey("digests.id"), primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey("resources.id"), primary_key=True)


class TagQuery(db.Model):
    __tablename__ = "tag_queries"
    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id"), nullable=False)
    query = db.Column(db.Text, nullable=False)

    tag = db.relationship("Tag", backref="tag_queries")


# ── Admin setup ─────────────────────────────────────────────────────────────

admin = Admin(app, name="anews Admin")

# Resource is the main table — include most columns, inline tags
class ResourceView(ModelView):
    column_list = ("id", "source_id", "url", "title", "resource_type",
                   "published_at", "created_at", "summary")
    column_searchable_list = ("url", "title", "summary", "tldr")

    def search_placeholder(self):
        return "Search url, title, summary, tldr..."


admin.add_view(ResourceView(Resource, db.session))
admin.add_view(ModelView(Feed, db.session))
admin.add_view(ModelView(Tag, db.session))
admin.add_view(ArticleView(Article, db.session))
admin.add_view(PodcastEpisodeView(PodcastEpisode, db.session))
admin.add_view(ModelView(NewsletterIssue, db.session))
admin.add_view(ModelView(Digest, db.session))
# read-only lookup tables
admin.add_view(ModelView(NewsletterIssueResource, db.session, endpoint="newsletter_issue_resources"))
admin.add_view(ModelView(DigestResource, db.session, endpoint="digest_resources"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
