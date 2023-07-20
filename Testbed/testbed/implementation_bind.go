package testbed

import (
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"testbed/testbed/templates"
	"text/template"
)

type bind struct {
	container    *Container
	templatesDir string
}

func newBind(templatesDir string, container *Container) bind {
	return bind{
		templatesDir: templatesDir,
		container:    container,
	}
}

func (b bind) reload() error {
	execResult, err := b.container.Exec([]string{"rndc", "reload"})
	if err != nil {
		if err != nil {
			return err
		}
	}
	reloadOK, err := regexp.MatchString("server reload successful", execResult.StdOut)
	if err != nil {
		return err
	}
	if !reloadOK {
		err = errors.New(fmt.Sprintf("bind could not be reloaded successfully: \nstdout: %s\nstderr: %s", execResult.StdOut, execResult.StdErr))
		return err
	}
	return nil
}

func (b bind) start() error {
	execResult, err := b.container.Exec([]string{"named", "-u", "bind", "-4", "-d", "2"})
	if err != nil {
		return err
	}
	if execResult.StdOut != "" {
		return errors.New(fmt.Sprintf("bind could not be started successfully: \nstdout: %s\nstderr: %s", execResult.StdOut, execResult.StdErr))
	}
	return nil
}

func (b bind) flushCache() error {
	execResult, err := b.container.Exec([]string{"rndc", "flush"})
	if err != nil {
		return err
	}
	flushedOK, err := regexp.MatchString("", execResult.StdOut)
	if err != nil {
		return err
	}
	if !flushedOK {
		err = errors.New(fmt.Sprintf("bind cache could not be flushed successfully: \nstdout: %s\nstderr: %s", execResult.StdOut, execResult.StdErr))
		return err
	}
	return nil
}

func (b bind) filterQueries(queryLog []byte) []byte {
	var queries []string
	lines := strings.Split(string(queryLog), "\n")
	for _, line := range lines {
		matched, err := regexp.MatchString("(query:)", line)
		if err != nil {
			panic(err)
		}
		if matched {
			queries = append(queries, line)
		}
	}
	return []byte(strings.Join(queries, "\n"))
}

func (b bind) SetConfig(qmin, reload bool) error {
	tmpl, err := template.ParseFiles(filepath.Join(b.templatesDir, "named.conf.options"))
	if err != nil {
		panic(err)
	}
	dest, err := os.Create(filepath.Join(b.container.Config, "named.conf.options"))
	if err != nil {
		panic(err)
	}
	options := &templates.Resolver{
		QMin: "off",
	}
	if qmin {
		options.QMin = "relaxed"
	}
	err = tmpl.Execute(dest, options)
	if err != nil {
		panic(err)
	}
	if reload {
		err := b.reload()
		if err != nil {
			return err
		}
	}
	return nil
}
