package config

import (
	"fmt"
	"path/filepath"
	"strings"
)

type ResolverInput struct {
	IP             string
	Version        string
	Implementation string
}

type Resolver struct {
	ID             string
	IP             string
	Implementation *implementation
	Dir            string
	Logs           string
	Config         string
}

func (c *Config) newResolver(build string, input *ResolverInput) (*Resolver, error) {
	var err error
	impl, err := getImplementation(input.Implementation, input.Version)
	id := generateResolverID(impl)
	dir := filepath.Join(build, id)
	return &Resolver{
		ID:             id,
		IP:             input.IP,
		Implementation: impl,
		Dir:            dir,
		Logs:           filepath.Join(dir, "logs"),
		Config:         filepath.Join(dir, "config"),
	}, err
}

func generateResolverID(impl *implementation) string {
	version := impl.Version
	if impl.Name == "powerdns" {
		version = strings.Join(strings.Split(version, ""), ".")
	}
	return fmt.Sprintf("resolver-%s-%s", impl.Name, version)
}
