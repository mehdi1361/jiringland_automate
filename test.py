import pymongo
import requests

client = pymongo.MongoClient(host="127.0.0.1", port=27017)
db = client.jiringland


def set_time():
    import datetime
    import time
    from datetime import timedelta
    # dt = datetime.datetime(2019, 2, 25, 23, 23)

    dt = datetime.datetime.now() + timedelta(days=7)
    print int(time.mktime(dt.timetuple()))
    return int(time.mktime(dt.timetuple()))


def set_players_league_category():
    url = "https://fourbknd.com:3020/parse/functions/SetPlayersLeagueCategory"

    payload = "{\n    \"username\": \"Ahmadhp\",\n    \"receipt\": \"{\\\"orderId\\\": \\\"70317409562607\\\"," \
              " \\\"purchaseToken\\\": \\\"70317409562607\\\", \\\"developerPayload\\\": \\\"\\\", \\\"" \
              "packageName\\\": \\\"com.darchingames.clicker\\\", \\\"purchaseState\\\": 0, \\\"purchaseTime" \
              "\\\": 1458771298856, \\\"productId\\\": \\\"pack_2\\\"}\"\n}"
    headers = {
        'Content-Type': "application/json",
        'X-Parse-Application-Id': "emrBjnhYAs8QkWWp8apnpGvsDrMxgsgdEUMABPhC",
        'Cache-Control': "no-cache"
    }

    response = requests.request("POST", url, data=payload, headers=headers)

    print(response.text)


def populate_leagues():
    url = "https://fourbknd.com:3020/parse/functions/populateLeagues"

    payload = "{\n    \"username\": \"Ahmadhp\",\n    \"receipt\": \"{\\\"orderId\\\": \\\"70317409562607\\\", \\\"" \
              "purchaseToken\\\": \\\"70317409562607\\\", \\\"developerPayload\\\": \\\"\\\", \\\"" \
              "packageName\\\": \\\"com.darchingames.clicker\\\", \\\"purchaseState\\\": 0, \\\"purchaseTime\\\":" \
              " 1458771298856, \\\"productId\\\": \\\"pack_2\\\"}\"\n}"

    headers = {
        'Content-Type': "application/json",
        'X-Parse-Application-Id': "emrBjnhYAs8QkWWp8apnpGvsDrMxgsgdEUMABPhC",
        'Cache-Control': "no-cache",
        'Postman-Token': "971513c4-50b2-4b73-badc-d6d3ed38f5fd"
    }

    response = requests.request("POST", url, data=payload, headers=headers)

    print(response.text)


def player_backup():
    player_data_backup = db["PlayerDataBackup"]
    player_data_dump = db["PlayerDataDump"]

    for p in db.PlayerData.find():
        player_data_backup.insert(p)
        player_data_dump.insert(p)


def league_backup():
    leagues_backup = db["LeaguesBackup"]
    leagues_dump = db["LeaguesDump"]
    leagues_backup.remove({})
    leagues_dump.remove({})

    for l in db.Leagues.find():
        leagues_backup.insert(l)
        leagues_dump.insert(l)
        print l


def main():
    # create player backup
    player_backup()

    # create league backup
    league_backup()

    db.Global.update_one(
        {
            '_id': "FkTyBpGctP"
        },
        {
            '$set':
                {
                    'lastLeague': "A1#999999",
                    'lastLeagueCount': 60
                }
        },
        upsert=False
    )
    db.Leagues.remove({})

    # * Call "SetPlayersLeagueCategory" API-> Calculate each user status based on his/her
    # gem and population then assign them to one of 13 league types.
    set_players_league_category()

    # * Call "populateLeagues" API-> Divide users of each one of 13 league type to paraller leaderboards.
    populate_leagues()

    for elem in db.PlayerDataDump.find():
        print elem['leagueType']
        db.PlayerData.update_one(
            {
                '_id': elem['_id']
            },
            {
                '$set': {
                    'leagueType': elem['leagueType'],
                    'previousRank': elem['previousRank'],
                    'previousLeague': elem['previousLeague'],
                    'leagueResultShown': elem['leagueResultShown'],
                    'tokenCount': elem['tokenCount'],
                    'PrizeTokenCollection': elem['PrizeTokenCollection']
                }
            }
        )

    for league in db.LeaguesDump.find():
        db.Leagues.insert(league)


if __name__ == '__main__':
    set_time()
