#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import datetime
from distutils.util import strtobool
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy.exc import SQLAlchemyError

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)

#----------------------------------------------------------------------------#
# Logging Config.
#----------------------------------------------------------------------------#

file_handler = FileHandler('error.log')
file_handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
app.logger.setLevel(logging.INFO)
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    website_link = db.Column(db.String(120))
    status = db.Column(db.Boolean,default=True)
    status_comment = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Venue')

    def add(self):
      db.session.add(self)
      db.session.commit()

    def update(self):
      db.session.update(self)
      db.session.commit()

    def delete(self):
      db.session.delete(self)
      db.session.commit()

    def __repr__(self):
      return f'<Object: Venue, Name: {self.name}, Address: {self.address}, City: {self.city}, State: {self.state}, Phone: {self.phone}, Image: {self.image_link}, Facebook: {self.facebook_link}, Website: {self.website_link}, Status: {self.status}, Status Comment: {self.status_comment}>'

    @property
    def set(self):
      return {'id':self.id,
              'name':self.name,
              'city':self.city,
              'state':self.state,
              'address':self.address,
              'phone':self.phone,
              'image_link':self.image_link,
              'facebook_link':self.facebook_link,
              'website_link':self.website_link,
              'status':self.status,
              'status':self.status_comment
      }
    
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    status = db.Column(db.Boolean())
    status_comment = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Artist')

    def add(self):
      db.session.add(self)
      db.session.commit()

    def update(self):
      db.session.update(self)
      db.session.commit()

    def delete(self):
      db.session.delete(self)
      db.session.commit()

    def __repr__(self):
      return f'<Object: Artist, Name: {self.name}, City: {self.city}, State: {self.state}, Phone: {self.phone}, Image: {self.image_link}, Facebook: {self.facebook_link}, Website: {self.website_link}, Status: {self.status}, Status Comment: {self.status_comment}>'

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    venue = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    artist = db.Column(db.Integer, db.ForeignKey('Artist.id'))

    def add(self):
      db.session.add(self)
      db.session.commit()

    def update(self):
      db.session.update(self)
      db.session.commit()

    def delete(self):
      db.session.delete(self)
      db.session.commit()

    def __repr__(self):
      return f'<Object: Venue, Time: {self.time}, Venue: {self.venue}, Artist: {self.artist}>'



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  
  venue_query = Venue.query.all()
  unique_locations = Venue.query.with_entities(Venue.city,Venue.state).distinct(Venue.city,Venue.state).all()
  data = []
  venues_list = []

  for location in unique_locations:
    for venue in venue_query:
      if(venue.city==location[0] and venue.state==location[1]):
        upcoming = db.session.query(Show).filter(Show.venue==venue.id).filter(Show.time>datetime.now()).all()
        venues_list.append({'id':venue.id,'name':venue.name,'num_upcoming_shows':len(upcoming)})
    data.append({'city':location.city,'state':location.state,'venues':venues_list})
    venues_list=[]

    app.logger.info(data)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  
  venue_query = Venue.query.filter(Venue.name.ilike('%'+request.form['search_term']+'%'))
  app.logger.info(venue_query)
  data = [];
  
  for venue in venue_query:
    upcoming = db.session.query(Show.Venue).filter(Show.venue==venue.id).filter(Show.time>datetime.now()).all()
    data.append({
      'id':venue.id,
      'name':venue.name,
      'num_upcoming_shows':len(upcoming)
      })

  response = {'count':len(data),'data':data}

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  venue = Venue.query.get(venue_id)
  data = []
  
  if venue is None:
    abort(404)
  else:
    upcoming = db.session.query(Show).join(Venue).filter(Show.venue==venue.id).filter(Show.time>datetime.now()).all()
    past = db.session.query(Show).join(Venue).filter(Show.venue==venue.id).filter(Show.time<datetime.now()).all()

    upcoming_shows = []
    past_shows = []

    for show in upcoming:
      upcoming_shows.append({
        'artist_id':show.artist,
        'artist_name':show.Artist.name,
        'artist_image_link':show.Artist.image_link,
        'start_time':show.time.strftime("%m/%d/%Y, %H:%M:%S")
        })

    for show in past:
      past_shows.append({
        'artist_id':show.artist,
        'artist_name':show.Artist.name,
        'artist_image_link':show.Artist.image_link,
        'start_time':show.time.strftime("%m/%d/%Y, %H:%M:%S")
        })

    data={
    'id':venue.id,
    'name':venue.name,
    'genres':venue.genres,
    'address':venue.address,
    'city':venue.city,
    'state':venue.state,
    'phone':venue.phone,
    'website':venue.website_link,
    'facebook_link':venue.facebook_link,
    'seeking_talent':venue.status,
    'seeking_description':venue.status_comment,
    'image_link':venue.image_link,
    'past_shows':past_shows,
    'past_shows_count':len(past_shows),
    'upcoming_shows':upcoming_shows,
    'upcoming_shows_count':len(upcoming_shows)
    }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    new_venue = Venue(
      name=request.form['name'],
      address=request.form['address'],
      city=request.form['city'],
      state=request.form['state'],
      phone=request.form['phone'],
      facebook_link=request.form['facebook_link'],
      image_link=request.form['image_link'],
      status=strtobool(request.form['status']),
      status_comment=request.form['status_comment'],
      genres = request.form['genres']
      )
    Venue.add(new_venue)
    app.logger.info(new_venue)
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except SQLAlchemyError as e:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  venue = Venue.query.get(venue_id)
  if venue_date is None:
    abort(404)
  else:
    Venue.delete(venue)

  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artist_query = Artist.query.all()
  app.logger.info(type(artist_query))
  data = []

  for artist in artist_query:
    data.append({'id':artist.id,'name':artist.name})

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  
  artist_query = Artist.query.filter(Artist.name.ilike('%'+request.form['search_term']+'%'))
  app.logger.info(artist_query)
  data = [];
  
  for artist in artist_query:
    upcoming = db.session.query(Show).filter(Show.artist==artist.id).filter(Show.time>datetime.now()).all()
    data.append({
      'id':artist.id,
      'name':artist.name,
      'num_upcoming_shows':len(upcoming)
      })

  response = {'count':len(data),'data':data}

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  
  artist = Artist.query.get(artist_id)
  data = []
  
  if artist is None:
    abort(404)
  else:
    upcoming = db.session.query(Show).join(Artist).filter(Show.artist==artist.id).filter(Show.time>datetime.now()).all()
    past = db.session.query(Show).join(Artist).filter(Show.artist==artist.id).filter(Show.time<datetime.now()).all()

    upcoming_shows = []
    past_shows = []

    for show in upcoming:
      upcoming_shows.append({
        'venue_id':show.venue,
        'venue_name':show.Venue.name,
        'artist_image_link':show.Venue.image_link,
        'start_time':show.time.strftime("%m/%d/%Y, %H:%M:%S")
        })

    for show in past:
      past_shows.append({
        'venue_id':show.venue,
        'venue_name':show.Venue.name,
        'artist_image_link':show.Venue.image_link,
        'start_time':show.time.strftime("%m/%d/%Y, %H:%M:%S")
        })

    data={
    'id':artist.id,
    'name':artist.name,
    'genres':artist.genres,
    'city':artist.city,
    'state':artist.state,
    'phone':artist.phone,
    'website':artist.website_link,
    'facebook_link':artist.facebook_link,
    'seeking_talent':artist.status,
    'seeking_description':artist.status_comment,
    'image_link':artist.image_link,
    'past_shows':past_shows,
    'past_shows_count':len(past_shows),
    'upcoming_shows':upcoming_shows,
    'upcoming_shows_count':len(upcoming_shows)
    }

  app.logger.info(data)

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  try:
    new_artist = Artist(
      name=request.form['name'],
      city=request.form['city'],
      state=request.form['state'],
      phone=request.form['phone'],
      facebook_link=request.form['facebook_link'],
      image_link=request.form['image_link'],
      website_link=request.form['website_link'],
      status=strtobool(request.form['status']),
      status_comment=request.form['status_comment'],
      genres=request.form['genres']
      )
    Artist.add(new_artist)
    app.logger.info(new_artist)
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except SQLAlchemyError as e:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  show_query = Show.query.join(Venue).join(Artist).all()
  data = []

  for show in show_query:
    data.append({
      'venue_id':show.venue,
      'venue_name':show.Venue.name,
      'artist_id':show.artist,
      'artist_name':show.Artist.name,
      'artist_image_link':show.Artist.image_link,
      'start_time':show.time.strftime("%m/%d/%Y, %H:%M:%S")
      })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  try:
    app.logger.info("Trying to create a new show")
    app.logger.info(request.form['start_time'])
    app.logger.info(int(request.form['artist_id']))
    app.logger.info(int(request.form['venue_id']))
    new_show = Show(
      artist=int(request.form['artist_id']),
      venue=int(request.form['venue_id']),
      time=request.form['start_time'],
      )
    Show.add(new_show)
    app.logger.info(new_show)
    flash('Show was successfully listed!')
  except SQLAlchemyError as e:
    flash('An error occurred. Show could not be listed.')

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
