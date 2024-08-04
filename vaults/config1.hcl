ui            = true
api_addr      = "https://127.0.0.1:8300"
disable_mlock = true

storage "file" {
  path = "vaults/data/vault1"
}

listener "tcp" {
  address       = "127.0.0.1:8300"
  tls_disable   = 1
}

