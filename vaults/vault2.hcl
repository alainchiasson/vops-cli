ui            = true
api_addr      = "https://127.0.0.1:8320"
disable_mlock = true

storage "file" {
  path = "vaults/data/vault2"
}

listener "tcp" {
  address       = "127.0.0.1:8320"
  tls_disable   = 1
}

