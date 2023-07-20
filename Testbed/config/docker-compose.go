package config

type DockerCompose struct {
	Nameservers []*Nameserver
	Resolvers   []*Resolver
	Client      *Client
}
