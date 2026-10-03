
# Flight Ticket Booking Application

A full-stack flight booking web app with two separate user domains — passengers
who search and book, and admins who manage inventory and read the resulting
feedback. Built with Flask, MySQL, and server-rendered Jinja templates.

The part worth looking at is the admin analytics: passenger feedback is run
through VADER sentiment analysis and summarised as a pie chart, so an admin
sees sentiment distribution rather than a wall of comments.

---

## Features

**Passenger side**

- Sign up / log in (bcrypt-hashed passwords)
- Search flights by route and date
- Book seats, with availability decremented on booking
- View personal booking history
- Submit free-text feedback

**Admin side**

- Separate login, gated behind a registration key
- Add and remove flights
- View bookings per flight
- Read raw feedback
- **Sentiment analytics** — feedback classified positive / negative / neutral
  and rendered as a pie chart

## Architecture

```
app.py              Flask routes — /user/* and /admin/* namespaces
nlp.py              VADER sentiment analysis + chart generation
helpers/            config loading
templates/
  user/             passenger-facing pages
  admin/            admin-facing pages
Static/             generated sentiment chart
```

Access control is enforced with two decorators rather than inline checks, which
keeps the route bodies clean and makes it hard to forget a check:

```python
@app.route('/admin/add_flight', methods=['GET', 'POST'])
@login_required_admin
def add_flight():
    ...
```

### Sentiment analysis

```python
sia = SentimentIntensityAnalyzer()
sentiment_score = sia.polarity_scores(feedback)
```

VADER returns a `compound` score in `[-1, 1]`, thresholded at ±0.05 into three
buckets. VADER is rule-based and lexicon-driven — no training data needed, which
is the right call for free-text feedback where there's nothing labelled to train
on.

## Database schema

MySQL, database name `flight_application`. There's no migration file in the repo
— these are the tables the queries expect:

| Table | Columns |
|---|---|
| `users` | `id`, `username`, `email`, `password` (bcrypt hash) |
| `admins` | `id`, `username`, `email`, `password` (bcrypt hash) |
| `flights` | `id`, `flight_number`, `date`, `time`, `price`, `seat_count`, `` `from` ``, `` `to` `` |
| `bookings` | `id`, `user_id`, `flight_id`, `seats_booked` |
| `feedback` | `id`, `user_id`, `message` |

Note `from` and `to` are backtick-quoted in the queries — both are reserved
words in SQL.

## Running it

```bash
pip install flask mysql-connector-python flask-bcrypt pyyaml nltk matplotlib
python -c "import nltk; nltk.download('vader_lexicon')"
```

Create the MySQL database and tables above, then create `helpers/config.yaml`:

```yaml
SECRET_KEY: '<a long random hex string>'
key: '<the key required to register a new admin>'
```

```bash
python app.py
```

## Security notes

Things this gets right:

- Passwords are **bcrypt-hashed**, never stored or compared in plaintext
- All SQL uses **parameterized queries** (`%s` placeholders), so user input
  can't alter query structure
- Admin and passenger sessions are separate, enforced by distinct decorators

Things to fix:

- **`helpers/config.yaml` is committed to version control.** It should be
  gitignored, with a `config.example.yaml` committed in its place. The
  `SECRET_KEY` signs session cookies — anyone who has it can forge a session.
- **Database credentials are hardcoded** in `app.py` and `nlp.py`. They belong
  in the config file (or environment variables) alongside the other secrets.
- **The chart output path in `nlp.py` is an absolute Windows path**, so chart
  generation only works on the original machine.

## What I'd change

- **A `requirements.txt`** — dependencies are currently only discoverable by
  reading the imports.
- **A schema file** (`schema.sql`) so the database can be recreated in one
  command instead of by reverse-engineering the queries.
- **Replace the bare `except:`** on the DB connection — it prints a message and
  continues, leaving `db` undefined so the real failure surfaces later and
  somewhere less obvious.
- **Move the sentiment chart to generate on request** rather than writing a PNG
  to disk — it's regenerated per view anyway, and the file path is the main
  thing tying this app to one machine.

## Built with

Python · Flask · MySQL · NLTK (VADER) · bcrypt · matplotlib · Jinja2 · HTML/CSS
