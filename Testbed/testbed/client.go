package testbed

import (
	"fmt"
	"testbed/config"
)

type Client struct {
	Nameserver string
	*Container
}

func newClient(clientConfig *config.Client) *Client {
	container := NewContainer(clientConfig.ID, clientConfig.Dir, clientConfig.ID)
	return &Client{
		Container:  container,
		Nameserver: clientConfig.Nameserver,
	}
}

func (c *Client) Query(zone, record string, resolver *Resolver) string {
	execResult, err := c.Exec([]string{"dig", "+tries=1", "+ignore", fmt.Sprintf("@%s", resolver.ip), zone, record})
	if err != nil {
		panic(err)
	}
	return execResult.StdOut
}
