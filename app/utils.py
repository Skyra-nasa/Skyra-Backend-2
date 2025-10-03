def interact_with_llm(activity:str = None, responseJson:dict = None):
    from app.llm import interact_llm
    weather_values = {key: responseJson[key]['mean'] for key in responseJson if 'mean' in responseJson  [key]}
    response = interact_llm(activity, weather_values)
    return response