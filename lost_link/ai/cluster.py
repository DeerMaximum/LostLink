from hdbscan import HDBSCAN
from langchain_chroma import Chroma
import pandas as pd
import operator

from lost_link.settings import Settings


class Cluster:

    def __init__(self, vector_db: Chroma, settings: Settings):
        self._vector_db = vector_db
        self.cluster_data = pd.DataFrame()
        self._settings = settings

    def _cleanup_cluster(self):
        for source in self.cluster_data["source"].unique():
            assigned_clusters: dict[int, int] = {}

            for row in self.cluster_data.loc[self.cluster_data['source'] == source].itertuples():
                assigned_clusters[row.cluster] = assigned_clusters.get(row.cluster, 0) + 1

            if assigned_clusters.get(-1):
                assigned_clusters[-1] = 0

            target_cluster = max(assigned_clusters.items(), key=operator.itemgetter(1))[0]
            self.cluster_data.loc[self.cluster_data['source'] == source, "cluster"] = target_cluster

        #Fix all -1 clusters
        last_cluster_id = max(self.cluster_data["cluster"].unique())
        for source in self.cluster_data["source"].unique():
            if self.cluster_data.loc[self.cluster_data['source'] == source, "cluster"].iloc[0] != -1:
                continue
            last_cluster_id += 1
            self.cluster_data.loc[self.cluster_data['source'] == source, "cluster"] = last_cluster_id


    def create_cluster(self):
        embedding_entries = self._vector_db.get(include=["metadatas", "embeddings"])

        hdbscan_settings = self._settings.get(Settings.GROUP_KEY_HDBSCAN, {})
        min_samples = hdbscan_settings.get(Settings.KEY_HDBSCAN_MIN_SAMPLES, 4)
        min_cluster_size = hdbscan_settings.get(Settings.KEY_HDBSCAN_MIN_CLUSTER_SIZE, 10)
        cluster_selection_epsilon = hdbscan_settings.get(Settings.KEY_HDBSCAN_SELECTION_EPSILON, 0.2)

        hdb = HDBSCAN( min_samples=min_samples, min_cluster_size=min_cluster_size, metric='euclidean', cluster_selection_epsilon=cluster_selection_epsilon).fit(
            embedding_entries.get("embeddings", []))

        self.cluster_data["id"] = embedding_entries.get("ids", [])
        self.cluster_data["source"] = [x["source"] for x in embedding_entries.get("metadatas", [])]
        self.cluster_data["cluster"] = hdb.labels_.astype(int)

        self._cleanup_cluster()

    def get_nearest_cluster_for_vectors(self, vectors: list[list[float]]) -> int:
        vector_results: dict[int, int] = {}

        for vector in vectors:
            result = self._vector_db.similarity_search_by_vector(vector, k=1)[0]
            nearest_embeddings_id = result.metadata["id"]
            nearest_cluster = self.cluster_data.loc[self.cluster_data['id'] == nearest_embeddings_id, "cluster"].iloc[0]
            vector_results[nearest_cluster] = vector_results.get(nearest_cluster, 0) + 1

        return max(vector_results.items(), key=operator.itemgetter(1))[0]

    def get_file_ids_for_cluster(self, cluster_id: int) -> list[str]:
        return self.cluster_data.loc[self.cluster_data['cluster'] == cluster_id, "source"].unique().tolist()