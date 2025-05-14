provider "google" {
  project     = var.project_id
  region      = var.region
  credentials = file("service-account-key.json")
}

# BigQuery Dataset
resource "google_bigquery_dataset" "loyalty_dataset" {
  dataset_id  = "loyalty_analytics"
  description = "Dataset for loyalty analytics data"
  location    = var.region
}

# Cloud Storage Bucket
resource "google_storage_bucket" "data_lake" {
  name     = "${var.project_id}-loyalty-data-lake"
  location = var.region
}

# Compute Engine VM for Spark
resource "google_compute_instance" "spark_instance" {
  name         = "spark-master"
  machine_type = "e2-standard-2"
  zone         = "${var.region}-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12-bookworm-v20250513"
    }
  }

  network_interface {
    network = "default"
    access_config {}
  }
}