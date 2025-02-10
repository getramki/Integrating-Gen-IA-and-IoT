import json
import boto3

sw = boto3.client('iotsitewise')

def lambda_handler(event, context):
    agent = event['agent']
    actionGroup = event['actionGroup']
    function = event['function']
    parameters = event.get('parameters', [])
    
    wind_farms = ['Adair','Bethel','CampSprings','Deerfield','Fenton','PleasantValley' ]
    entries=[]
    
    try:
        for wf in wind_farms:
            for i in range(1, 11):
                if i < 10:
                    wtg = "WTG-0" + str(i)
                elif i >= 10:
                    wtg = "WTG-" + str(i)
                
                entryId_pwr = str(wf + '-' + wtg + '-ActivePower')
                # print(entryId_pwr)
                
                propertyAlias_pwr = str('/' + wf + '/' + wtg + '/ActivePower')
                # print(propertyAlias_pwr)
                
                entry_power = {
                    'entryId': entryId_pwr,
                    'propertyAlias': propertyAlias_pwr
                }
                
                # print(entry_power)
                
                entryId_err = str(wf + '-' + wtg + '-ErrorStatus')
                propertyAlias_err = str('/' + wf + '/' + wtg + '/ErrorStatus')
                
                entry_status = {
                    'entryId': entryId_err,
                    'propertyAlias': propertyAlias_err
                }
                
                entries.append(entry_power)
                entries.append(entry_status)
                
        # Batch get asset property values
        response = sw.batch_get_asset_property_value(entries=entries)
        
        # Initialize variables
        ap_Adair = ap_Bethel = ap_CampSprings = ap_Deerfield = ap_Fenton = ap_PleasantValley = 0
        run_count_Adair = run_count_Bethel = run_count_CampSprings = run_count_Deerfield = run_count_Fenton = run_count_PleasantValley = 0
        err_count_Adair = err_count_Bethel = err_count_CampSprings = err_count_Deerfield = err_count_Fenton = err_count_PleasantValley = 0
        
        # Process the response
        for entry in response['successEntries']:
            entry_id = entry['entryId']
            
            if 'ActivePower' in entry_id:
                value = entry['assetPropertyValue']['value']['doubleValue']
                if 'Adair' in entry_id:
                    ap_Adair = ap_Adair + value
                elif 'Bethel' in entry_id:
                    ap_Bethel = ap_Bethel + value
                elif 'CampSprings' in entry_id:
                    ap_CampSprings = ap_CampSprings + value
                elif 'Deerfield' in entry_id:
                    ap_Deerfield = ap_Deerfield + value
                elif 'Fenton' in entry_id:
                    ap_Fenton = ap_Fenton + value
                elif 'PleasantValley' in entry_id:
                    ap_PleasantValley = ap_PleasantValley + value
            elif 'ErrorStatus' in entry_id:
                value = entry['assetPropertyValue']['value']['booleanValue']
                if 'Adair' in entry_id:
                    if value == False:
                        run_count_Adair = run_count_Adair + 1
                    elif value == True:
                        err_count_Adair = err_count_Adair + 1
                elif 'Bethel' in entry_id:
                    if value == False:
                        run_count_Bethel = run_count_Bethel + 1
                    elif value == True:
                        err_count_Bethel = err_count_Bethel + 1
                elif 'CampSprings' in entry_id:
                    if value == False:
                        run_count_CampSprings = run_count_CampSprings + 1
                    elif value == True:
                        err_count_CampSprings = err_count_CampSprings + 1
                elif 'Deerfield' in entry_id:
                    if value == False:
                        run_count_Deerfield = run_count_Deerfield + 1
                    elif value == True:
                        err_count_Deerfield = err_count_Deerfield + 1
                elif 'Fenton' in entry_id:
                    if value == False:
                        run_count_Fenton = run_count_Fenton + 1
                    elif value == True:
                        err_count_Fenton = err_count_Fenton + 1
                elif 'PleasantValley' in entry_id:
                    if value == False:
                        run_count_PleasantValley = run_count_PleasantValley + 1
                    elif value == True:
                        err_count_PleasantValley = err_count_PleasantValley + 1
                
        total_power = ap_Adair + ap_Bethel + ap_CampSprings + ap_Deerfield + ap_Fenton + ap_PleasantValley
        wtgs_running = run_count_Adair + run_count_Bethel + run_count_CampSprings + run_count_Deerfield + run_count_Fenton + run_count_PleasantValley
        wtgs_error = err_count_Adair + err_count_Bethel + err_count_CampSprings + err_count_Deerfield + err_count_Fenton + err_count_PleasantValley
        
        print ('Total Power: '+ str(round(float(total_power/1000), 2)))
        print ('WTGs Running: '+ str(wtgs_running))
        print ('WTGs Errot: '+ str(wtgs_error))
        
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
                    "The Summary data of all Wind Farms is as Follows: " + 
                    "The total power generated across all wind farms is " + str(round(float(total_power/1000), 2)) + 
                    " MW. The breakdown is as follows: Adair (" + str(round(float(ap_Adair/1000),2)) + 
                    " MW), Bethel ("+ str(round(float(ap_Bethel/1000),2)) + 
                    " MW), CampSprings (" + str(round(float(ap_CampSprings/1000),2)) + 
                    " MW), Deerfield (" + str(round(float(ap_Deerfield/1000),2)) + 
                    " MW), Fenton (" + str(round(float(ap_Fenton/1000),2)) + 
                    " MW), and PleasantValley (" + str(round(float(ap_PleasantValley/1000),2)) + " MW). " + 
                    "There are " + str(wtgs_running) +" wind turbine generators in running condition: " + 
                    " Adair (" + str(run_count_Adair) + 
                    "), Bethel (" + str(run_count_Bethel) + 
                    "), CampSprings (" + str(run_count_CampSprings) + 
                    "), Deerfield (" + str(run_count_Deerfield) + 
                    "), Fenton (" + str(run_count_Fenton) + 
                    "), and PleasantValley (" + str(run_count_PleasantValley) + "). " + 
                    "There are " + str(wtgs_error) +" wind turbine generators in error condition: " + 
                    "Adair (" + str(err_count_Adair) + 
                    "), Bethel (" + str(err_count_Bethel) + 
                    "), CampSprings (" + str(err_count_CampSprings) + 
                    "), Deerfield (" + str(err_count_Deerfield) + 
                    "), Fenton (" + str(err_count_Fenton) + 
                    "), and PleasantValley (" + str(err_count_PleasantValley) + ")."
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
