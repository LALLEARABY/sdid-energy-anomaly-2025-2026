from G3_data_mining.data_access.fetch_data import fetch_historical_data
from G3_data_mining.preprocessing.scaling import scale_data
from G3_data_mining.modeling.pca import apply_pca
from G3_data_mining.modeling.clustering import run_dbscan
from G3_data_mining.visualization.plot import plot_clusters


def main():
    print("Démarrage du pipeline de data mining du groupe G3")

    df = fetch_historical_data()
    X_scaled, scaler = scale_data(df)
    X_pca, pca = apply_pca(X_scaled)
    labels, params = run_dbscan(X_pca)

    plot_clusters(X_pca, labels)

    print("Pipeline G3 terminé avec succès")

if __name__ == "__main__":
    main()
