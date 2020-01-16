"""

This file contains functions that preprocess the secondspectrum
tracking data to fit our visualization needs.

"""
import numpy as np
import pandas as pd


def change_player_coord_format(ss_df):
    """
    Changes columns 'awayPlayers' and 'homePlayers' player location
    data representation. Changes list of dictionaries to a dictionary.
    The dictionary has player_ids as keys and player locations as values.
    
    Args:
        ss_df: secondspectrum tracking data dataframe, is modified inplace
    
    """
    ss_df['awayPlayers'] = ss_df['awayPlayers'].apply(lambda players_coords:    \
                                                      { d['playerId']: d['xyz'] \
                                                      for d in players_coords } \
                                                     )
    ss_df['homePlayers'] = ss_df['homePlayers'].apply(lambda players_coords:    \
                                                      { d['playerId']: d['xyz'] \
                                                      for d in players_coords } \
                                                     )

def ball_possession(ss_df):
    """
    Labels which player and team has possession of ball.
    0 for home team. 1 for away team.
    
    Args:
        ss_df: secondspectrum tracking data dataframe,
               is modified inplace to have columns poss_player, poss_team
    """
    ss_df['poss_player'] = ""
    ss_df['poss_team'] = -1
    ss_df['poss_team'] = ss_df['poss_team'].astype(int)
    
    # secondspectrum documentation tells us event
    # "TOUCH" represents ball possession by player
    # hence, forward fill the columns based on "TOUCH" event
    current_player = ""
    current_team = -1
    for index,row in ss_df.iterrows():
        if row['eventType'] == 'TOUCH':
            current_player = row['playerId']
            current_team = 0 if current_player in row['homePlayers'] else 1
        ss_df.at[index, 'poss_player'] = current_player
        ss_df.at[index, 'poss_team'] = current_team

        
def label_possession_idx(ss_df):
    """
    Labels the possessions with an index.
    
    Args:
        ss_df: secondspectrum tracking data dataframe,
               is modified inplace to have column poss_idx
    """
    ss_df['poss_idx'] = 0
    ss_df['poss_idx'] = ss_df['poss_idx'].astype(int)
    
    idx = 0
    current_team = -1
    for index,row in ss_df.iterrows():
        if row['poss_team'] != current_team:
            current_team = row['poss_team']
            idx += 1
        
        ss_df.at[index,'poss_idx'] = idx
        
        
def label_half_court(ss_df):
    """
    Labels which half-court the possession happens in.
    0 for left half-court. 1 for right half-court.
    Also trims the possession time-series data to only
    include data of front-court. Back-court data points
    are omitted. Our visualization only cares about 
    front-court possessions.
    
    Args:
        ss_df: secondspectrum tracking data dataframe,
               is modified inplace to have column half_court_idx
               
    """
    ss_df['half_court_idx'] = -1
    ss_df['half_court_idx'] = ss_df['half_court_idx'].astype(int)
    
    
    teamA, teamB = -1, -1
    halfcourtA, halfcourtB = -1, -1
    
    # find the first "SHOT" event, corresponding team & front-court
    for index, row in ss_df.iterrows():
        if row['eventType'] == 'SHOT':
            break
    teamA = row['poss_team']
    halfcourtA = 0 if row['ball']['xyz'][0] < 0 else 1
    halfcourtB = int(not halfcourtA)
    
    
    halfcourt = halfcourtA
    poss_team = teamA
    for index, row in ss_df.iterrows():
        if row['period'] > 2:
            halfcourtA = int(not halfcourtA)
            halfcourtB = int(not halfcourtB)
        if row['poss_team'] != poss_team:
            halfcourt = halfcourtB if halfcourt == halfcourtA else halfcourtA
            poss_team = row['poss_team']
        
        ss_df.at[index, 'half_court_idx'] = halfcourt
        



def convert_coordinates(ss_df):
    """
    Returns a dataframe with a column of converted coordinates.
    Converted coordinates units are 10 x feet.
    Converted coordinates are such that basket is on top of screen.
    
    :param ss_df: secondspectrum tracking data dataframe
    :return: modified dataframe with 
    """
    
    