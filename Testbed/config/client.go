package config

import "path/filepath"

type ClientInput struct {
	ID         string
	IP         string
	Nameserver string
}

type Client struct {
	ID         string
	IP         string
	Nameserver string
	Dir        string
}

func (c *Config) newClient(build string, input *ClientInput) *Client {
	return &Client{
		ID:         input.ID,
		IP:         input.IP,
		Nameserver: input.Nameserver,
		Dir:        filepath.Join(build, input.ID),
	}
}
