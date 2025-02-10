import json
import boto3

sw = boto3.client('iotsitewise')

def lambda_handler(event, context):
    agent = event['agent']
    actionGroup = event['actionGroup']
    function = event['function']
    parameters = event.get('parameters', [])
    
    for parameter in parameters:
        if parameter['name'] == 'Wind-Farm-Name':
            wind_farm_name = parameter['value']
        elif parameter['name'] == 'Wind-Turbine-ID':
            wind_turbine_id = int(parameter['value'])

    if wind_turbine_id < 10:
        wtg = "WTG-0" + str(wind_turbine_id)
    elif wind_turbine_id >= 10:
        wtg = "WTG-" + str(wind_turbine_id)
    
    power_dict = sw.get_asset_property_value(
        # assetId='string',
        # propertyId='string',
        propertyAlias='/' + wind_farm_name + '/'+ wtg + '/ActivePower'
    )
    
    power = ((power_dict.get('propertyValue')).get('value')).get('doubleValue')
    
    ws_dict = sw.get_asset_property_value(
        # assetId='string',
        # propertyId='string',
        propertyAlias='/' + wind_farm_name + '/'+ wtg + '/WindSpeed'
    )
    
    wind_speed = ((ws_dict.get('propertyValue')).get('value')).get('doubleValue')
    
    # power = 1234.34
    # wind_speed = 14.56
    
    print(parameters)
    # Execute your business logic here. For more information, refer to: https://docs.aws.amazon.com/bedrock/latest/userguide/agents-lambda.html
    responseBody =  {
        "TEXT": {
            "body": "Wind Turbine " + wtg + " in the wind farm " + wind_farm_name + " is generating " + str(round(float(power),2)) +" KW power at the wind speed " + str(round(float(wind_speed),2)) + " meters/sec."
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
    
    print("Response: {}".format(function_response))

    return function_response
