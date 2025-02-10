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
                'propertyAlias': '/' + wind_farm_name + '/' + wtg + '/Energy'
            },
            {
                'entryId': '2',
                'propertyAlias': '/' + wind_farm_name + '/' + wtg + '/AmbientTemp'
            },
            {
                'entryId': '3',
                'propertyAlias': '/' + wind_farm_name + '/' + wtg + '/BearingTemp'
            },
            {
                'entryId': '4',
                'propertyAlias': '/' + wind_farm_name + '/' + wtg + '/GearBoxVibration'
            },
            {
                'entryId': '5',
                'propertyAlias': '/' + wind_farm_name + '/' + wtg + '/RotorSpeed'
            },
            {
                'entryId': '6',
                'propertyAlias': '/' + wind_farm_name + '/' + wtg + '/WindDirection'
            }
        ]
        
        # Batch get asset property values
        response = sw.batch_get_asset_property_value(entries=entries)
        
        # Initialize variables
        energy = ambient_temp = bearing_temp = gear_box_vibration = rotor_speed = wind_direction = None
        
        # Process the response
        for entry in response['successEntries']:
            entry_id = entry['entryId']
            value = entry['assetPropertyValue']['value']['doubleValue']
            
            if entry_id == '1':
                energy = value
            elif entry_id == '2':
                ambient_temp = value
            elif entry_id == '3':
                bearing_temp = value
            elif entry_id == '4':
                gear_box_vibration = value
            elif entry_id == '5':
                rotor_speed = value
            elif entry_id == '6':
                wind_direction = value
        
        # Handle errors if needed
        for error in response['errorEntries']:
            print(f"Error in entry {error['entryId']}: {error['errorMessage']}")
        
        # Handle skipped entries if needed
        for skipped in response['skippedEntries']:
            print(f"Skipped entry {skipped['entryId']}: {skipped['completionStatus']}")
            
        # print(parameters)
        
        responseBody = {
            "TEXT": {
                "body": (
                    "The measurments of Wind Turbine " + wtg + " in the wind farm " + wind_farm_name + " are The Energy Generated is" + str(round(float(energy), 2)) + " KWH, "
                    "The ambient temperature is " + str(round(float(ambient_temp), 2)) + "°C, "
                    "bearing temperature is " + str(round(float(bearing_temp), 2)) + "°C, "
                    "gear box vibration is " + str(round(float(gear_box_vibration), 2)) + " mm/s, "
                    "rotor speed is " + str(round(float(rotor_speed), 2)) + " meters/sec, "
                    "and wind direction is " + str(round(float(wind_direction), 2)) + " degrees."
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
