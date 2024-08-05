ui            = true
api_addr      = "https://127.0.0.1:8330"
disable_mlock = true

storage "file" {
  path = "vaults/data/vault3"
}

listener "tcp" {
  address       = "127.0.0.1:8330"
  tls_disable   = 1
}

