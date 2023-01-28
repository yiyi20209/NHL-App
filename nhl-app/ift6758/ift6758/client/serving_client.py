import json
import requests
import pandas as pd
import logging
from utils import preprocess,transform


logger = logging.getLogger(__name__)


class ServingClient:
    def __init__(self, ip: str = "0.0.0.0", port: int = 4000, features=None):
        self.base_url = f"http://{ip}:{port}"
        logger.info(f"Initializing client; base URL: {self.base_url}")

        if features is None:
            features = ["distance"]
        self.features = features

        # any other potential initialization

    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Formats the inputs into an appropriate payload for a POST request, and queries the
        prediction service. Retrieves the response from the server, and processes it back into a
        dataframe that corresponds index-wise to the input dataframe.
        
        Args:
            X (Dataframe): Input dataframe to submit to the prediction service.
        """
        
        #preprocess data 
        # df_test=X[(X['season']==20192020) & (X['gameType']=='R')]
        
        X_logreg = X[['distanceNet_or_shotDistance', 'shot_angle_absolute']]
        
        X_xgb = preprocess(X)
        # df_train_xg = preprocess(df_test, split=False)
        # return df_train_xg.loc[::,df_train_xg.columns!='goal']
        X_xgb = transform(X_xgb)
        # df_test_xg = transform(X_train, df_train_xg.loc[::,df_train_xg.columns!='goal'], y_train)
        # df_test_yg=df_test['goal']
        # df_test_xg = df_test_xg.T.reset_index(drop = True).T
        # return df_test_xg
        # response = None

        # try:
        #     response = requests.post(self.base_url+'/predict', json=json.loads(df_test_xg.loc[:5].to_json()))
        #     logger.info(response.json())
        #     logger.info("SUCCESS: Generated predictions!")
        #     return response.json()
        # except Exception as e:
        #     logger.error(e)     
        
        req = '{"X_logreg":' + X_logreg.to_json() + ', "X_xgb":' + X_xgb.to_json() + '}'
            
        response = requests.post(self.base_url+'/predict', json=json.loads(req))
        logger.info(response.json())
        logger.info("SUCCESS: Generated predictions!")
        return response.json()
        
        

    def logs(self) -> dict:
        """Get server logs"""
        
        response = requests.get(self.base_url+'/logs')
        logger.info(response.json())
        return response.json()


    def download_registry_model(self, workspace: str, model: str, version: str) -> dict:
        """
        Triggers a "model swap" in the service; the workspace, model, and model version are
        specified and the service looks for this model in the model registry and tries to
        download it. 

        See more here:

            https://www.comet.ml/docs/python-sdk/API/#apidownload_registry_model
        
        Args:
            workspace (str): The Comet ML workspace
            model (str): The model in the Comet ML registry to download
            version (str): The model version to download
        """
        
        response = requests.post(self.base_url+'/download_registry_model',
                                 json={'workspace': workspace, 'model': model, 'version': version})
        logger.info("SUCCESS: Model downloaded!")
        # return response.json()
        