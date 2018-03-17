#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    This module get name and album name and artists of track from
    one or more  spotify's playlist of user and stored in csv or txt
    file

    TODO: problem in show utf8 in select list
    TODO: show all list without check for owner or two list
"""

import getopt
import sys

import spotipy
import spotipy.util as util
from pick import pick
from prettytable import PrettyTable

from user_data import (SCOPE, SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,
                       SPOTIPY_REDIRECT_URI, USERNAME)


def make_choose_list(username, playlists):
    """
        make list of username playlist for selectable list
        get playlist list response from spotify
        get username for detect owner of playlist
        return list of playlist's name for pick library
        return dictionary of name and key of playlist
    """
    dictionary_of_playlist = {}
    list_title = []
    for playlist in playlists['items']:
        if playlist['owner']['id'] == username:
            dictionary_of_playlist[playlist['id']] = playlist['name']
            list_title.append(playlist['name'])
        else:
            print "Can't get token for", username
    return dictionary_of_playlist, list_title


def show_choice_list(dictionary_of_playlist, list_title):
    """
        show selectable list
        get list_title for pick library
        get dictionary_of_playlist for detect key or keys of playlists selected
        return keys or key of selected playlist
    """
    title = """Please choose your playlist
    (press SPACE to mark, ENTER to continue): """
    selected = pick(list_title, title, multi_select=True, min_selection_count=1)
    list_selected = []
    print selected
    for name_selected, key in selected:
        for playlist_id, name in dictionary_of_playlist.iteritems():
            if name_selected == name:
                list_selected.append(playlist_id)

    return list_selected


def write_in_csv(results, file_name):
    """
        get results as respons for playlist's key from spotify to extract
        track name, album name, artists
        get file_name for name of file data writted in
        save csv file in directory script run in it
    """
    tracks = results['tracks']['items']
    with open(file_name+'.csv', 'wb') as csv_output:
        csv_output.write("track name, album name, artists")
        for track in tracks:
            track_name = track['track']['name']
            album_name = track['track']['album']['name']
            artists = track['track']['artists']
            artists_name = ""
            for artist in artists:
                artists_name += artist['name'].encode('utf-8') + '/'
            csv_output.write(track_name.encode('utf-8') + "," +
                             album_name.encode('utf-8') +
                             "," + artists_name[:-1] + "\n")
            artists_name = ''

        csv_output.close()


def write_in_table(results, file_name):
    """
        get results as respons for playlist's key from spotify to extract
        track name, album name, artists
        get file_name for name of file data writted in
        save txt(table -> pretty table)file in directory script run in it
    """
    # create table
    table = PrettyTable(["number", "track name", "album name", "artists"])
    table.align["track name"] = "l"
    table.align["album name"] = "l"
    table.align["artists"] = "l"
    table.padding_width = 1
    tracks = results['tracks']['items']
    index = 1
    for track in tracks:
        artists = track['track']['artists']
        artists_name = ""
        for artist in artists:
            artists_name += artist['name'].encode('utf-8') + '/'
        table.add_row([index,
                       track['track']['name'].encode('utf-8'),
                       track['track']['album']['name'].encode('utf-8'),
                       artists_name[:-1]])
        index += 1
    with open(file_name+".txt", 'wb') as table_file:
        table_file.write(str(table))

    table_file.close()


def create_file_list(type_output, file_name):
    """
        get type_output for type of input csv or table in txt file
        get file_name for name file stored in directory script run in it
        connect to spotify API and get respons and depend of type_output
        run write_in_csv or write_in_table
    """
    token = util.prompt_for_user_token(USERNAME, SCOPE, client_id=SPOTIPY_CLIENT_ID,
                                       client_secret=SPOTIPY_CLIENT_SECRET,
                                       redirect_uri=SPOTIPY_REDIRECT_URI)

    if token:
        spotify = spotipy.Spotify(auth=token)
        playlists = spotify.user_playlists(USERNAME)
        dic_playlist, title_list = make_choose_list(USERNAME, playlists)
        list_playlist_id = show_choice_list(dic_playlist, title_list)
        print list_playlist_id
        results = spotify.user_playlist(USERNAME, list_playlist_id[0], fields="tracks,next")
        if file_name == "":
            file_name = "output"
        if type_output == "":
            type_output = "csv"
        if type_output in ("csv", "CSV"):
            write_in_csv(results, file_name)
        elif type_output in ("table", "TABLE"):
            write_in_table(results, file_name)


def main(argv):
    """
        get file name and type of output from script argument
        and run create_file_list() method
    """
    type_output = ''
    output_name = ''
    try:
        opts, args = getopt.getopt(argv, "ht:o:", ["help", "output-type=",
                                                   "output-name="])
    except getopt.GetoptError:
        print "get_music_name_playlist.py -t <output type (table or csv)> -o <output name>"
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print "get_music_name_playlist.py -t <output type (table or csv)> -o <output name>"
            sys.exit()
        elif opt in ("-t", "--output-type"):
            type_output = arg
        elif opt in ("-o", "--output-name"):
            output_name = arg
    create_file_list(type_output, output_name)

if __name__ == '__main__':
    main(sys.argv[1:])
