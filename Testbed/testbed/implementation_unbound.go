package testbed

import (
	"fmt"
	"github.com/pkg/errors"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"testbed/testbed/templates"
	"text/template"
)

type unbound struct {
	templatesDir string
	container    *Container
}

func newUnbound(templatesDir string, container *Container) unbound {
	return unbound{
		templatesDir: templatesDir,
		container:    container,
	}
}

func (u unbound) reload() error {
	execResult, err := u.container.Exec([]string{"unbound-control", "reload"})
	if err != nil {
		return err
	}
	reloadOK, err := regexp.MatchString("ok", execResult.StdOut)
	if err != nil {
		return err
	}
	if !reloadOK {
		err = errors.New(fmt.Sprintf("unbound cache could not be restarted successfully: \nstdout: %s\nstderr: %s", execResult.StdOut, execResult.StdErr))
		return err
	}
	return nil
}

func (u unbound) start() error {
	execResult, err := u.container.Exec([]string{"unbound-control-setup"})
	if err != nil {
		panic(err)
	}
	matched, err := regexp.MatchString("Setup success", execResult.StdOut)
	if err != nil {
		panic(err)
	}
	if !matched {
		err = errors.New(fmt.Sprintf("unbound setup not executed successfully: \nstdout: %s\nstderr: %s", execResult.StdOut, execResult.StdErr))
		return err
	}
	execResult, err = u.container.Exec([]string{"unbound-control", "start"})
	if err != nil {
		panic(err)
	}
	matched, err = regexp.MatchString("", execResult.StdOut)
	if err != nil {
		panic(err)
	}
	if !matched {
		err = errors.New(fmt.Sprintf("unbound start not executed successfully: \nstdout: %s\nstderr: %s", execResult.StdOut, execResult.StdErr))
		return err
	}
	return nil
}

func (u unbound) flushCache() error {
	return u.reload()
}

func (u unbound) filterQueries(queryLog []byte) []byte {
	var queries []string
	lines := strings.Split(string(queryLog), "\n")
	for _, line := range lines {
		matched, err := regexp.MatchString("(query:|reply:)", line)
		if err != nil {
			panic(err)
		}
		if matched {
			queries = append(queries, line)
		}
	}
	return []byte(strings.Join(queries, "\n"))
}

func (u unbound) SetConfig(qmin, reload bool) error {
	tmpl, err := template.ParseFiles(filepath.Join(u.templatesDir, "unbound.conf"))
	if err != nil {
		return err
	}
	dest, err := os.Create(filepath.Join(u.container.Config, "unbound.conf"))
	if err != nil {
		return err
	}
	options := &templates.Resolver{
		QMin: "no",
	}
	if qmin {
		options.QMin = "yes"
	}
	err = tmpl.Execute(dest, options)
	if err != nil {
		panic(err)
	}
	if reload {
		if err := u.reload(); err != nil {
			return err
		}
	}
	return nil
}
