ui            = true
api_addr      = "https://127.0.0.1:8340"
disable_mlock = true

storage "file" {
  path = "vaults/data/vault14"
}

listener "tcp" {
  address       = "127.0.0.1:8340"
  tls_disable   = 1
}

