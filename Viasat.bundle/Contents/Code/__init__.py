PREFIX = '/video/viasat'

ART = 'art-default.png'
ICON = 'icon-default.png'

API_BASE = 'http://playapi.mtgx.tv/v3'
CHANNEL_API = '/'.join([API_BASE, 'channels'])
SHOW_API = '/'.join([API_BASE, 'formats'])
SEASON_API = '/'.join([API_BASE, 'seasons'])
EPISODE_API = '/'.join([API_BASE, 'videos'])


####################################################################################################

# This function is initially called by the PMS framework to initialize the plugin. This includes
# setting up the Plugin static instance along with the displayed artwork.
def Start():
    Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')
    Plugin.AddViewGroup('List', viewMode='List', mediaType='items')

    ObjectContainer.art = R(ART)
    ObjectContainer.title1 = 'Viasat'
    ObjectContainer.view_group = 'List'

    DirectoryObject.thumb = R(ICON)
    DirectoryObject.art = R(ART)
    VideoClipObject.thumb = R(ICON)
    VideoClipObject.art = R(ART)


# This main function will setup the displayed items.
@handler(PREFIX, 'Viasat', ICON, ART)
def MainMenu():

    oc = ObjectContainer()

    oc.add(DirectoryObject(
        key=Callback(ChannelsList),
        title=L('Channels Menu Title'),
        summary='',
        thumb=R('icon-channel.png')))
    oc.add(DirectoryObject(
        key=Callback(ShowsList),
        title=L('Shows Menu Title'),
        summary='',
        thumb=R('icon-channel.png')))
    oc.add(PrefsObject(
        title=L('Preferences Menu Title'), 
        thumb=R('icon-prefs.png')))

    return oc


@route('%s/channels' % PREFIX)
def ChannelsList():
    oc = ObjectContainer(title1=L('Channels Menu Title'))

    try:
        channels = JSON.ObjectFromURL(CHANNEL_API + '?country=%s' % Prefs['site'])
    except:
        return oc

    for channel in channels['_embedded']['channels']:
        oc.add(DirectoryObject(
            key=Callback(ChannelShows, channel_id=channel['id']),
            title=channel['name'],
            summary=channel['summary'],
            thumb=R('icon-channel.png')))

    if len(oc) < 1:
        Log('No channels found')
        return ObjectContainer(header='Empty', message='No channels available at the moment.')

    return oc

@route('%s/shows' % PREFIX)
def ShowsList():
    oc = ObjectContainer(title1=L('Shows Menu Title'))

    try:
        shows = JSON.ObjectFromURL(SHOW_API + '?country=%s' % Prefs['site'])['_embedded']['formats']
    except:
        return oc

    for show in shows:
        # oc.add(TVShowObject(
        #     key=Callback(ShowSeasons, show_id=show['id']),
        #     rating_key=show['_links']['self']['href'],
        #     title=show['title'],
        #     summary=show['summary'],
        #     thumb=Resource.ContentsOfURLWithFallback(show['image'], R('icon-channel.png')),
        #     source_title=show['content_owner']))
        oc.add(DirectoryObject(
            key=Callback(ShowSeasons, show_id=show['id']),
            title=show['title'],
            summary=show['summary'],
            thumb=Resource.ContentsOfURLWithFallback(show['image'], R('icon-channel.png'))))

    if len(oc) < 1:
        Log('No shows found')
        return ObjectContainer(header='Empty', message='No shows available at the moment.')

    return oc


@route('%s/channels/shows' % PREFIX)
def ChannelShows(channel_id):
    oc = ObjectContainer(title1=L('Shows Menu Title'))

    try:
        shows = JSON.ObjectFromURL('{endpoint}?channel={id}'.format(endpoint=SHOW_API, id=channel_id))['_embedded']['formats']
    except:
        return ObjectContainer(header='Empty', message='No shows available at the moment.')

    for show in shows:
        # oc.add(TVShowObject(
        #     key=Callback(ShowSeasons, show_id=show['id']),
        #     rating_key=show['_links']['self']['href'],
        #     title=show['title'],
        #     summary=show['summary'],
        #     thumb=Resource.ContentsOfURLWithFallback(show['image'], R('icon-channel.png')),
        #     source_title=show['content_owner']))
        oc.add(DirectoryObject(
            key=Callback(ShowSeasons, show_id=show['id']),
            title=show['title'],
            summary=show['summary'],
            thumb=Resource.ContentsOfURLWithFallback(show['image'], R('icon-channel.png'))))

    if len(oc) < 1:
        Log('No shows found')
        return ObjectContainer(header='Empty', message='No shows available at the moment.')

    return oc

@route('%s/shows/seasons' % PREFIX)
def ShowSeasons(show_id):
    oc = ObjectContainer(title1=L('Seasons Menu Title'), no_cache=True)

    try:
        seasons = JSON.ObjectFromURL('{endpoint}?format={id}'.format(endpoint=SEASON_API, id=show_id))['_embedded']['seasons']
    except:
        Log('Error while retrieving seasons for show {}'.format(show_id))
        return ObjectContainer(header='Empty', message='No seasons available at the moment')

    for season in seasons:
        # try:
        #     episode_count = int(JSON.ObjectFromURL(EPISODE_API + '?season=%d' % season['id'])['count']['total_items'])
        # except:
        #     episode_count = None

        # try:
        #     show = JSON.ObjectFromURL('{endpoint}/{id}'.format(endpoint=SHOW_API, id=show_id))
        # except:
        #     show = {'title': None, 'image': None}

        # oc.add(SeasonObject(
        #     key=Callback(SeasonEpisodes, season_id=season['id']),
        #     rating_key=season['_links']['self']['href'],
        #     title=season['title'],
        #     show=show['title'],
        #     index=show_id,
        #     summary=season['season_summary'],
        #     thumb=Resource.ContentsOfURLWithFallback(season['_links']['image']['href'].format(size='480x320'), R('icon-channel.png')),
        #     art=Resource.ContentsOfURLWithFallback(show['image'], R('icon-channel.png')),
        #     episode_count=episode_count))
        oc.add(DirectoryObject(
            key=Callback(
                SeasonEpisodes, 
                season_id=season['id'], 
                season_img=season['_links']['image']['href'].format(size='480x320'),
                page=1),
            title=season['title'],
            summary=season['season_summary'],
            thumb=Resource.ContentsOfURLWithFallback(season['_links']['image']['href'].format(size='480x320'), R('icon-channel.png'))))

    if len(oc) < 1:
        Log('No seasons found')
        return ObjectContainer(header='Empty', message='No seasons available at the moment.')

    return oc


@route('%s/seasons/episodes' % PREFIX)
def SeasonEpisodes(season_id, season_img, page):
    oc = ObjectContainer(title1=L('Episodes Menu Title'))
    page = int(page)

    try:
        res = JSON.ObjectFromURL('{endpoint}?season={id}&page={page}'.format(
            endpoint=EPISODE_API, 
            id=season_id,
            page=page))
        episodes = res['_embedded']['videos']
    except:
        return ObjectContainer(header='Empty', message='No shows available at the moment.')

    for episode in episodes:
        try:
            air_date = Datetime.ParseDate(episode['broadcasts'][0]['air_at']).date()
        except:
            air_date = None

        # try:
        #     show = JSON.ObjectFromURL('{endpoint}/{id}'.format(endpoint=SHOW_API, id=episode['format_id']))
        # except:
        #     show = {'title': None}

        # try:
        #     stream = JSON.ObjectFromURL(episode['_links']['stream']['href'])
        # except:
        #     stream = None

        # try:
        #     duration = int(episode['duration']) * 1000
        # except:
        #     duration = None
        
        # oc.add(EpisodeObject(
        #     url=episode['_links']['self']['href'],
        #     title=episode['title'],
        #     summary=episode['summary'],
        #     originally_available_at=air_date,
        #     show=show['title'],
        #     season=episode['season_id'],
        #     thumb=Resource.ContentsOfURLWithFallback(episode['_links']['image']['href'].format(size='480x320'), R('icon-channel.png')),
        #     duration=duration))

        title = episode['title']
        if air_date:
            title += ' ({})'.format(air_date)

        oc.add(VideoClipObject(
            url=episode['_links']['self']['href'],
            title=title,
            summary=episode['summary'],
            thumb=Resource.ContentsOfURLWithFallback(episode['_links']['image']['href'].format(size='480x320'), R('icon-channel.png'))))

    Log('Total pages: {total}; Current page: {current}'.format(
        total=res['count']['total_pages'],
        current=page))

    if int(res['count']['total_pages']) > page:
        oc.add(DirectoryObject(
            key=Callback(SeasonEpisodes, season_id=season_id, season_img=season_img, page=page+1),
            title='Next page'))

    if len(oc) < 1:
        Log('No episodes found')
        return ObjectContainer(header='Empty', message='No episodes available at the moment.')

    return oc
