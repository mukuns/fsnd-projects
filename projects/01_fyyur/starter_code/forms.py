from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, IntegerField
from wtforms.validators import DataRequired, AnyOf, URL
from enums import Genre, State


class ShowsForm(FlaskForm):
    artist_id = IntegerField(
        'artist_id', validators=[DataRequired()]
    )
    venue_id = IntegerField(
        'venue_id', validators=[DataRequired()]
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default=datetime.today()
    )


class ShowByArtistForm(FlaskForm):
    artist_search_term = IntegerField(
        'artist_id', validators=[DataRequired()]
    )


class ShowByVenueForm(FlaskForm):
    venue_search_term = IntegerField(
        'artist_id', validators=[DataRequired()]
    )


state_choices = [

]


class VenueForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=State.choices()
    )
    phone = StringField(
        'phone', validators=[DataRequired()]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired()],
        choices=Genre.choices()
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    website = StringField(
        'website_link', validators=[URL()]
    )
    seeking_talent = BooleanField(
        'seeking_talent', default=True
    )
    seeking_description = StringField(
        'seeking_description'
    )

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        if not set(self.genres.data).issubset(dict(Genre.choices()).keys()):
            self.genres.errors.append('Invalid genre.')
            return False
        if self.state.data not in dict(State.choices()).keys():
            self.state.errors.append('Invalid state.')
            return False
        # if pass validation
        return True


class ArtistForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=State.choices()
    )
    phone = StringField(
        # TODO implement validation logic for state
        'phone', validators=[DataRequired()],
    )
    image_link = StringField(
        'image_link', validators=[URL()]
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired()],
        choices=Genre.choices()
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    website = StringField(
        'website', validators=[URL()]
    )
    seeking_venue = BooleanField(
        'seeking_venue', default=False
    )
    seeking_description = StringField(
        'seeking_description'
    )
# TODO IMPLEMENT NEW ARTIST FORM AND NEW SHOW FORM
