import json
import boto3

sw = boto3.client('iotsitewise')

def lambda_handler(event, context):
    agent = event['agent']
    actionGroup = event['actionGroup']
    function = event['function']
    parameters = event.get('parameters', [])
    
    wind_farm_name = wind_turbine_id = None
    
    try:
        for parameter in parameters:
            if parameter['name'] == 'Wind-Farm-Name':
                wind_farm_name = parameter['value']
            elif parameter['name'] == 'Wind-Turbine-ID':
                wind_turbine_id = int(parameter['value'])
    
        if wind_turbine_id < 10:
            wtg = "WTG-0" + str(wind_turbine_id)
        elif wind_turbine_id >= 10:
            wtg = "WTG-" + str(wind_turbine_id)
        
        # Define the entries
        entries = [
            {
                'entryId': '1',
                'propertyAlias': '/' + wind_farm_name + '/' + wtg + '/BearingTemp'
            },
            {
                'entryId': '2',
                'propertyAlias': '/' + wind_farm_name + '/' + wtg + '/GearBoxVibration'
            },
            {
                'entryId': '3',
                'propertyAlias': '/' + wind_farm_name + '/' + wtg + '/ErrorCode'
            },
            {
                'entryId': '4',
                'propertyAlias': '/' + wind_farm_name + '/' + wtg + '/ErrorStatus'
            }
        ]
        
        # Batch get asset property values
        response = sw.batch_get_asset_property_value(entries=entries)
        
        # Initialize variables
        bearing_temp = gear_box_vibration = error_code = error_status = None
        
        # Process the response
        for entry in response['successEntries']:
            entry_id = entry['entryId']
            if entry_id == '1':
                value = entry['assetPropertyValue']['value']['doubleValue']
                bearing_temp = value
            elif entry_id == '2':
                value = entry['assetPropertyValue']['value']['doubleValue']
                gear_box_vibration = value
            elif entry_id == '3':
                value = entry['assetPropertyValue']['value']['integerValue']
                error_code = value
            elif entry_id == '4':
                value = entry['assetPropertyValue']['value']['booleanValue']
                error_status = value
        
        # Handle errors if needed
        for error in response['errorEntries']:
            print(f"Error in entry {error['entryId']}: {error['errorMessage']}")
        
        # Handle skipped entries if needed
        for skipped in response['skippedEntries']:
            print(f"Skipped entry {skipped['entryId']}: {skipped['completionStatus']}")
            
        # print(parameters)
        error_str = ""
        
        if error_status == True:
            if error_code == 1014:
                error_str = "Error in the Wind Turbine " + wtg + " in the wind farm " + wind_farm_name + "is Bearing Temperature High, it is " + str(round(float(bearing_temp),2)) + ", which is above normal range of 60-90 °C"
            elif error_code == 1023:
                error_str = "Error in the Wind Turbine " + wtg + " in the wind farm " + wind_farm_name + "is Gear Box Vibration High, it is " + str(round(float(gear_box_vibration),2)) + ", which is above normal range of 1-10 mm/sec"
        
        responseBody = {
            "TEXT": {
                "body": (
                    error_str
                )
            }
        }
    
        action_response = {
            'actionGroup': actionGroup,
            'function': function,
            'functionResponse': {
                'responseBody': responseBody
            }
    
        }
    
        function_response = {'response': action_response, 'messageVersion': event['messageVersion']}
        
    except Exception as e:
        responseBody = {
            "TEXT": {
                "body": (
                    f"An error occurred: {e}"
                )
            }
        }
    
        action_response = {
            'actionGroup': actionGroup,
            'function': function,
            'functionResponse': {
                'responseBody': responseBody
            }
    
        }
        
        function_response = {'response': action_response, 'messageVersion': event['messageVersion']}
        print(f"An error occurred: {e}")
    
    
    # print("Response: {}".format(function_response))

    return function_response
