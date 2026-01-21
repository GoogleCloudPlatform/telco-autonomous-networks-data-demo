
resource "google_discovery_engine_data_store" "rca_rules" {
  location                     = "global"
  data_store_id                = "rca_rules"
  display_name                 = "Rules for processing incidents in telco network."
  industry_vertical            = "GENERIC"
  content_config               = "NO_CONTENT"
  solution_types               = ["SOLUTION_TYPE_SEARCH"]
  project                      = var.project_id
  create_advanced_site_search  = false
  skip_default_schema_creation = true
}

resource "google_discovery_engine_schema" "rca_rules_schema" {
  location      = google_discovery_engine_data_store.rca_rules.location
  data_store_id = google_discovery_engine_data_store.rca_rules.data_store_id
  schema_id     = "schema-id"
  json_schema   = file("${path.module}/vertex-ai-schema/rca-rules.json")
}

resource "google_discovery_engine_search_engine" "rca_rules_search_engine" {
  engine_id = "rca_rules_search"
  collection_id = "default_collection"
  location = google_discovery_engine_data_store.rca_rules.location
  display_name = "RCA Rules Search"
  data_store_ids = [google_discovery_engine_data_store.rca_rules.data_store_id]
  search_engine_config {
  }
}
