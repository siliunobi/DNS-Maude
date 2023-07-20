package config

import (
	"fmt"
	"path/filepath"
)

type TestbedInput struct {
	Nameservers []*NameserverInput
	Resolvers   []*ResolverInput
	Client      *ClientInput
	Root        string
}

type Testbed struct {
	Templates   string
	Build       string
	Nameservers []*Nameserver
	Resolvers   []*Resolver
	Client      *Client
	QMin        bool
	Root        string
}

func (c *Config) LoadTestbedConfig() (*Testbed, error) {
	c.v.SetConfigFile(filepath.Join(c.path, "testbed.yaml"))
	if err := c.v.ReadInConfig(); err != nil {
		return nil, err
	}
	input := &TestbedInput{}
	if err := c.v.Unmarshal(input); err != nil {
		return nil, err
	}
	return c.newTestbed(input)
}

func (c *Config) newTestbed(input *TestbedInput) (*Testbed, error) {
	build := "build"
	var nameservers []*Nameserver
	for _, nameserverInput := range input.Nameservers {
		nameserver, err := c.newNameServer(build, nameserverInput)
		if err != nil {
			//TODO put user interaction into cmd package?
			fmt.Println(err)
		}
		nameservers = append(nameservers, nameserver)
	}
	var resolvers []*Resolver
	for _, resolverInput := range input.Resolvers {
		resolver, err := c.newResolver(build, resolverInput)
		if err != nil {
			//TODO put user interaction into cmd package?
			fmt.Println(err)
		}
		resolvers = append(resolvers, resolver)
	}
	return &Testbed{
		Templates:   filepath.Join("testbed", "templates"),
		Build:       build,
		Nameservers: nameservers,
		Resolvers:   resolvers,
		Client:      c.newClient(build, input.Client),
		QMin:        false,
		Root:        input.Root,
	}, nil
}
