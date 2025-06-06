# -*- coding: utf-8 -*-
"""Untitled6.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1vyrba_2P1XhF37reQwmvXhm6C4SJFOlo
"""

import os
import numpy as np
import pandas as pd
import pickle
from lightfm import LightFM
from lightfm.data import Dataset
from filelock import FileLock

class CFModel:
    def __init__(self, directory):
        self.modelPath = directory + 'bpr_model.pkl'
        self.mappingsPath = directory + 'mappings.pkl'
        self.csvPath = directory + 'data.csv'
        self.deleted_path = directory + 'deleted.pkl'
        self.lockPath = directory + 'model_lock.lock'
        
        self.model = None
        self.buyer_mapping = {}
        self.product_mapping = {}
        self.reverse_buyer_mapping = {}
        self.reverse_product_mapping = {}
        self.deleted_products = set()
        self.lock = FileLock(self.lockPath)
        os.makedirs(directory, exist_ok=True)

        print('hello')
        if self.is_trained():
            print("Model is pretrained")
            self.model, self.buyer_mapping, self.product_mapping, self.reverse_buyer_mapping, self.reverse_product_mapping = self.get_model()
            self.load_deleted_products()
        else:
            self.train()
            print("Model is not pretrained")

    def is_trained(self):
        import os
        return os.path.isfile(self.modelPath)

    def get_csv(self):
        return pd.read_csv(self.csvPath)

    def save_csv(self, df):
        df.to_csv(self.csvPath, index=False)

    def generate_mappings(self, df):
        unique_buyers = df["buyer"].unique()
        unique_products = df["product"].unique()

        self.buyer_mapping = {id_: idx for idx, id_ in enumerate(unique_buyers)}
        self.product_mapping = {id_: idx for idx, id_ in enumerate(unique_products)}
        self.reverse_buyer_mapping = {v: k for k, v in self.buyer_mapping.items()}
        self.reverse_product_mapping = {v: k for k, v in self.product_mapping.items()}

        df["buyer"] = df["buyer"].map(self.buyer_mapping)
        df["product"] = df["product"].map(self.product_mapping)

        return df

    def get_model(self):
        with open(self.modelPath, "rb") as f:
            model = pickle.load(f)

        with open(self.mappingsPath, "rb") as f:
            buyer_mapping, product_mapping, reverse_buyer_mapping, reverse_product_mapping = pickle.load(f)

        return model, buyer_mapping, product_mapping, reverse_buyer_mapping, reverse_product_mapping

    def save_model(self):
        with open(self.modelPath, "wb") as f:
            pickle.dump(self.model, f)

        with open(self.mappingsPath, "wb") as f:
            pickle.dump((self.buyer_mapping, self.product_mapping, self.reverse_buyer_mapping, self.reverse_product_mapping), f)

    def save_deleted_products(self):
        with open(self.deleted_path, "wb") as f:
            pickle.dump(self.deleted_products, f)

    def load_deleted_products(self):
        if os.path.exists(self.deleted_path):
            with open(self.deleted_path, "rb") as f:
                self.deleted_products = pickle.load(f)

    def train(self):
        self.deleted_products = set()
        self.save_deleted_products()
        df = self.get_csv()
        if df.empty:
            print("Training aborted: data.csv is empty.")
            return
        df = self.generate_mappings(df)
        dataset = Dataset()
        dataset.fit(users=self.buyer_mapping.values(), items=self.product_mapping.values())
        interactions, weights = dataset.build_interactions(
            [(row.buyer, row.product, row.weight) for row in df.itertuples(index=False)]
        )

        self.model = LightFM(loss='bpr')
        self.model.fit(interactions, sample_weight=weights, epochs=10, num_threads=4)
        self.save_model()

    def fit_partial(self, new_data):
        dataset = Dataset()
        dataset.fit(users=self.buyer_mapping.values(), items=self.product_mapping.values())

        interactions, weights = dataset.build_interactions(
            [(row.buyer, row.product, row.weight) for row in new_data.itertuples(index=False)]
        )

        self.model.fit_partial(interactions, sample_weight=weights, epochs=1, num_threads=4)
        self.save_model()

    def get_recommendations(self, user_id, num_recommendations=30):
        user_internal_id = self.buyer_mapping[user_id]

        product_ids = np.array(list(self.product_mapping.values()))
        scores = self.model.predict(user_internal_id, product_ids)

        top_indices = np.argsort(-scores)

        recommended_products = []
        for idx in top_indices:
            original_id = self.reverse_product_mapping.get(product_ids[idx])
            if original_id not in self.deleted_products:
                recommended_products.append(original_id)
            if len(recommended_products) >= num_recommendations:
                break

        return recommended_products

    def updateMappings(self, user_id, product_id):
        new_user = user_id not in self.buyer_mapping
        new_product = product_id not in self.product_mapping

        if new_user:
            new_uid = len(self.buyer_mapping)
            self.buyer_mapping[user_id] = new_uid
            self.reverse_buyer_mapping[new_uid] = user_id

        if new_product:
            new_pid = len(self.product_mapping)
            self.product_mapping[product_id] = new_pid
            self.reverse_product_mapping[new_pid] = product_id


    def add_interaction(self, buyer_id, product_id, weight=1.0):
        with self.lock:
            self.updateMappings(buyer_id, product_id)
            df = self.get_csv()
            new_data = pd.DataFrame({'buyer': [buyer_id], 'product': [product_id], 'weight': [weight]})
            df = pd.concat([df, new_data], ignore_index=True)
            self.save_csv(df)

            self.fit_partial(new_data)

    def delete_product(self, product_id):
        with self.lock:
            df = self.get_csv()
            df = df[df["product"] != product_id]
            self.save_csv(df)

            self.deleted_products.add(product_id)
            self.save_deleted_products()
'''

import os
import numpy as np
import pandas as pd
import pickle
from lightfm import LightFM
from lightfm.data import Dataset
from filelock import FileLock

class CFModel:
    def __init__(self, directory):
        self.modelPath = os.path.join(directory, 'bpr_model.pkl')
        self.mappingsPath = os.path.join(directory, 'mappings.pkl')
        self.csvPath = os.path.join(directory, 'data.csv')
        self.deleted_path = os.path.join(directory, 'deleted.pkl')
        self.lockPath = os.path.join(directory, 'model_lock.lock')

        self.model = None
        self.buyer_mapping = {}
        self.product_mapping = {}
        self.reverse_buyer_mapping = {}
        self.reverse_product_mapping = {}
        self.deleted_products = set()
        self.lock = FileLock(self.lockPath)

        #os.makedirs(directory, exist_ok=True)

        if self.is_trained():
            print("Model is pretrained")
            self.model, self.buyer_mapping, self.product_mapping, self.reverse_buyer_mapping, self.reverse_product_mapping = self.get_model()
            self.load_deleted_products()
        else:
            print("Model is not pretrained. Starting training...")
            self.train()

    def is_trained(self):
        return os.path.isfile(self.modelPath)

    def get_csv(self):
        if os.path.exists(self.csvPath):
            return pd.read_csv(self.csvPath)
        else:
            return pd.DataFrame(columns=["buyer", "product", "weight"])

    def save_csv(self, df):
        df.to_csv(self.csvPath, index=False)

    def generate_mappings(self, df):
        unique_buyers = df["buyer"].unique()
        unique_products = df["product"].unique()

        self.buyer_mapping = {id_: idx for idx, id_ in enumerate(unique_buyers)}
        self.product_mapping = {id_: idx for idx, id_ in enumerate(unique_products)}
        self.reverse_buyer_mapping = {v: k for k, v in self.buyer_mapping.items()}
        self.reverse_product_mapping = {v: k for k, v in self.product_mapping.items()}

        df["buyer"] = df["buyer"].map(self.buyer_mapping)
        df["product"] = df["product"].map(self.product_mapping)

        return df

    def get_model(self):
        with open(self.modelPath, "rb") as f:
            model = pickle.load(f)

        with open(self.mappingsPath, "rb") as f:
            buyer_mapping, product_mapping, reverse_buyer_mapping, reverse_product_mapping = pickle.load(f)

        return model, buyer_mapping, product_mapping, reverse_buyer_mapping, reverse_product_mapping

    def save_model(self):
        with open(self.modelPath, "wb") as f:
            pickle.dump(self.model, f)

        with open(self.mappingsPath, "wb") as f:
            pickle.dump((self.buyer_mapping, self.product_mapping, self.reverse_buyer_mapping, self.reverse_product_mapping), f)

    def save_deleted_products(self):
        with open(self.deleted_path, "wb") as f:
            pickle.dump(self.deleted_products, f)

    def load_deleted_products(self):
        if os.path.exists(self.deleted_path):
            with open(self.deleted_path, "rb") as f:
                self.deleted_products = pickle.load(f)

    def train(self):
        print("Training started...")
        
        self.deleted_products = set()  # Fix: do NOT overwrite self.delete_product
        self.save_deleted_products()

        df = self.get_csv()
        if df.empty:
            print("Training aborted: data.csv is empty.")
            return

        df = self.generate_mappings(df)

        dataset = Dataset()
        dataset.fit(users=self.buyer_mapping.values(), items=self.product_mapping.values())

        interactions, weights = dataset.build_interactions(
            [(row.buyer, row.product, row.weight) for row in df.itertuples(index=False)]
        )

        self.model = LightFM(loss='bpr')
        self.model.fit(interactions, sample_weight=weights, epochs=10, num_threads=1)

        self.save_model()
        print("Training completed and model saved.")


    def fit_partial(self, new_data):
        # Use raw IDs for fitting the Dataset
        raw_buyers = new_data['buyer'].tolist()
        raw_products = new_data['product'].tolist()

        dataset = Dataset()
        dataset.fit(users=self.buyer_mapping.keys(), items=self.product_mapping.keys())

        interactions, weights = dataset.build_interactions(
            [(buyer, product, weight) for buyer, product, weight in new_data.itertuples(index=False, name=None)]
        )

        self.model.fit_partial(interactions, sample_weight=weights, epochs=1, num_threads=1)
        self.save_model()


    def get_recommendations(self, user_id, num_recommendations=30):
        if user_id not in self.buyer_mapping:
            print(f"User {user_id} not found in mapping.")
            return []

        user_internal_id = self.buyer_mapping[user_id]
        product_ids = np.array(list(self.product_mapping.values()))
        scores = self.model.predict(user_internal_id, product_ids)
        top_indices = np.argsort(-scores)

        recommended_products = []
        for idx in top_indices:
            original_id = self.reverse_product_mapping.get(product_ids[idx])
            if original_id not in self.deleted_products:
                recommended_products.append(original_id)
            if len(recommended_products) >= num_recommendations:
                break

        return recommended_products

    def updateMappings(self, user_id, product_id):
        new_user = user_id not in self.buyer_mapping
        new_product = product_id not in self.product_mapping

        if new_user:
            new_uid = len(self.buyer_mapping)
            self.buyer_mapping[user_id] = new_uid
            self.reverse_buyer_mapping[new_uid] = user_id

        if new_product:
            new_pid = len(self.product_mapping)
            self.product_mapping[product_id] = new_pid
            self.reverse_product_mapping[new_pid] = product_id

    def add_interaction(self, buyer_id, product_id, weight=1.0):
        with self.lock:
            self.updateMappings(buyer_id, product_id)
            df = self.get_csv()
            new_data = pd.DataFrame({'buyer': [buyer_id], 'product': [product_id], 'weight': [weight]})
            df = pd.concat([df, new_data], ignore_index=True)
            self.save_csv(df)

            self.fit_partial(new_data)

    def delete_product(self, product_id):
        with self.lock:
            df = self.get_csv()
            df = df[df["product"] != product_id]
            self.save_csv(df)

            self.deleted_products.add(product_id)
            self.save_deleted_products()

#m = CFModel('intelliwear/recommendation/data2/')
#print(m.product_mapping)
#df = pd.read_csv("intelliwear/recommendation/data/data.csv")
#print(df.head())
'''