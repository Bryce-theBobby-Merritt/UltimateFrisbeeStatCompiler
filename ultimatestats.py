import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time #for time.wait(100) to make sure you dont go over call limit
import numpy as np

#hook up to the sheet
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('client_info.json', scope)
sheets_client = gspread.authorize(credentials)

def calculate_automatic_stats(sheet):
    print ('Working on: {}'.format(sheet.title))
    arr = np.array(sheet.get_all_values())
    arr.reshape(20, 14)
    rows, cols = arr.shape
    
    # per player stats
    for row in range(1, rows):
        arr[row][3] = int(arr[row][1]) + int(arr[row][2]) # O and D points combine to total poitns per player: working
        arr[row][8] = int(arr[row][6]) + int(arr[row][7]) # mark and downfield blocks combine to total blocks per player: working
        arr[row][11] = int(arr[row][9]) + int(arr[row][10]) # incomplete throws and drops become total turnovers: working

    # team-wide stats
    arr[3][13] = int(arr[1][13]) + int(arr[2][13]) # Team O Points + Team D points = Team Total Points: working

    for row in range(1, rows):
        team_assists = int(arr[4][13]) 
        team_assists += int(arr[row][4])
        arr[4][13] = int(team_assists) #team assists 

        team_goals = int(arr[5][13])
        team_goals += int(arr[row][5])
        arr[5][13] = int(team_goals) #team goals

        team_mark_blocks = int(arr[6][13])
        team_mark_blocks += int(arr[row][6])
        arr[6][13] = int(team_mark_blocks) #team mark blocks

        team_downfield_blocks = int(arr[7][13])
        team_downfield_blocks += int(arr[row][7])
        arr[7][13] = int(team_downfield_blocks) #team downfield blocks

        team_total_blocks = int(arr[8][13])
        team_total_blocks += int(arr[row][8])
        arr[8][13] = int(team_total_blocks) #team total blocks

        team_incomplete_throws = int(arr[9][13])
        team_incomplete_throws += int(arr[row][9])
        arr[9][13] = int(team_incomplete_throws) #team incomplete throws

        team_drops = int(arr[10][13])
        team_drops += int(arr[row][10])
        arr[10][13] = int(team_drops) #team drops

        team_total_turnovers = int(arr[11][13])
        team_total_turnovers += int(arr[row][11])
        arr[11][13] = int(team_total_turnovers) #team total turnovers
    
    return arr

def update_spreadsheet(sheet, arr):
    working_arr = arr
    arr_rows, arr_cols = arr.shape
    working_sheet = sheet
    cell_list = sheet.range('A1:N20')

    for cell in cell_list:
        cell.value = working_arr[(cell.row-1)][(cell.col-1)]
    sheet.update_cells(cell_list)
    print ('    Finished updating sheet: {}'.format(sheet.title))

    
def main():
    active_database = sheets_client.open('ulti_stats')
    all_sheets = active_database.worksheets()
    all_arrs = {}

    for sheet in range(1, len(all_sheets)):
        updated_stats = calculate_automatic_stats(all_sheets[sheet])
        all_arrs[all_sheets[sheet].title] = updated_stats
        update_spreadsheet(all_sheets[sheet], updated_stats)
    
    #do cumulative stats
    cumulative_sheet = all_sheets[0]
    print('Working on: {}'.format(cumulative_sheet.title))

    cumul_arr = np.array(cumulative_sheet.get_all_values())
    cumul_arr.reshape(20, 14)
    cumul_rows, cumul_cols = cumul_arr.shape
    for row in range(1, cumul_rows): #for each player
        for column in range(1, (cumul_cols - 2)): #for each stat 
            curr_stat = 0
            for game in all_arrs: #for each game
                curr_stat += int(all_arrs[game][row][column]) #the stat is incremented by the value of said stat in each individual game for that player
            cumul_arr[row][column] = curr_stat #update the cumulative array's value

    update_spreadsheet(all_sheets[0], cumul_arr) #send the cumulative array to google to update

if __name__ == '__main__':
    main()
    print('Done')
