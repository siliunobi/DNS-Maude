package testbed

import (
	"errors"
	"fmt"
	"path/filepath"
	"testbed/config"
)

type Resolver struct {
	Implementation
	*Container
	Dir string
}

func newResolver(resolverConfig *config.Resolver, templates string) *Resolver {
	container := NewContainer(resolverConfig.ID, resolverConfig.Dir, resolverConfig.IP)
	var implementation Implementation
	switch resolverConfig.Implementation.Name {
	case "bind":
		implementation = newBind(
			filepath.Join(templates, "resolver-bind"),
			container,
		)
	case "unbound":
		implementation = newUnbound(
			filepath.Join(templates, "resolver-unbound"),
			container,
		)
	case "powerdns":
		implementation = newPowerDNS(
			filepath.Join(templates, "resolver-powerdns"),
			container,
		)
	default:
		panic(errors.New(fmt.Sprintf("Implementation kind %s has no instantiation method yet.", resolverConfig.Implementation)))
	}
	return &Resolver{
		Implementation: implementation,
		Container:      container,
	}
}
