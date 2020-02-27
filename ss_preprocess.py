"""

This file contains functions that preprocess the secondspectrum
tracking data to fit our visualization needs.

"""
import numpy as np
import pandas as pd




def change_coord_format(ss_df):
    """
    Changes columns 'awayPlayers' and 'homePlayers' player location
    data representation. Changes list of dictionaries to a dictionary.
    The dictionary has player_ids as keys and player locations as values.
    Change column 'ball' data representation. Remove dictionary wrapper.
    
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
    ss_df['ball'] = ss_df['ball'].apply(lambda ball_d: ball_d['xyz'])

def label_possession(ss_df):
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
    halfcourtA = 0 if row['ball'][0] < 0 else 1
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
        
    
    # drop the back-court data for each possession
    drop_indices = []
    for index, row in ss_df.iterrows():
        half_court, ball_x = row['half_court_idx'], row['ball'][0]
        if (half_court == 0 and ball_x > 0):
            drop_indices.append(index)
        if (half_court == 1 and ball_x < 0):
            drop_indices.append(index)
    
    ss_df.drop(drop_indices, inplace=True)

    
    
# scaling matrix for left half-court
scaling_mat_left   = np.array([[-10,0],
                               [0, 10]])
    
scaling_mat_right  = np.array([[10, 0],
                               [0,-10]])
    
    
rotation_mat_left  = np.array([[0, 1],
                               [-1, 0]])
    
rotation_mat_right = np.array([[0, -1],
                               [1, 0]])

transform_left = scaling_mat_left @ rotation_mat_left
transform_right = scaling_mat_right @ rotation_mat_right
    
# matrix that inverts the y-axis range
translate_mat_left = np.array([[0, (470 - 47.5)]])

translate_mat_right = np.array([[0, - 47.5]])


def convert_coords_helper(coords: list):
    global transform_left, transform_right
    global translate_mat
    
    # only want x and y coordinates. drop z
    xy = np.asarray(coords[:2]).reshape(1,2)
    
    if coords[0] < 0:
        return list(xy @ transform_left + translate_mat_left)
    else:
        return list(xy @ transform_right + translate_mat_right)

def convert_coords_helper_players(player_coords: dict):
    
    transformed_coords = {}
    for player, coords in player_coords.items():
        
        if coords[0] < 0:
            transformed_coords[player] = convert_coords_helper(coords)
        else:
            transformed_coords[player] = convert_coords_helper(coords)
            
    return transformed_coords
    
    
def convert_coordinates(ss_df):
    """
    Returns a dataframe with a column of converted coordinates.
    Converted coordinates units are 10 x feet.
    Converted coordinates are such that basket is on top of screen.
    
    :param ss_df: secondspectrum tracking data dataframe
    :return: modified dataframe with 
    """
    
    
    ss_df['awayPlayers'] = ss_df['awayPlayers'].apply(lambda players_coords:  \
                                   convert_coords_helper_players(players_coords))
    
    ss_df['homePlayers'] = ss_df['homePlayers'].apply(lambda players_coords:  \
                                   convert_coords_helper_players(players_coords))
    
    ss_df['ball'] = ss_df['ball'].apply(lambda ball_coords:  \
                                        convert_coords_helper(ball_coords))
    

    