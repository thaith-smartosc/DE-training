provider "google" {
  credentials = file("de-training-d4-e60eece858ef.json")
  project     = "de-training-d4"
  region      = "asia-southeast1"
}

resource "google_compute_network" "vpc_network" {
  name = "terraform-network"
}

resource "google_compute_firewall" "default" {
  name    = "allow-ssh"
  network = google_compute_network.vpc_network.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
}

resource "google_compute_instance" "vm_instance" {
  name         = "vm-terraform"
  machine_type = "e2-micro"
  zone         = "asia-southeast1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = google_compute_network.vpc_network.name

    access_config {
      // Ephemeral public IP
    }
  }

  metadata = {
    ssh-keys = "compute-admin:${file("id_rsa.pub")}"
  }
}

# New resource for Google Cloud Storage bucket
resource "google_storage_bucket" "bucket" {
  name     = "terraform-bucket-d4"
  location = "asia-southeast1"
}

# Example: Binding storage admin role to a user (replace with your email)
resource "google_storage_bucket_iam_member" "member" {
  bucket = google_storage_bucket.bucket.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:terraform-admin@de-training-d4.iam.gserviceaccount.com"
}


