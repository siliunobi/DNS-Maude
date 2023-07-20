package testbed

import (
	"bytes"
	"context"
	"fmt"
	"github.com/docker/docker/api/types"
	"github.com/docker/docker/client"
	"github.com/docker/docker/pkg/stdcopy"
	"github.com/rs/zerolog"
	"io"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"time"
)

type Container struct {
	client              client.APIClient
	ctx                 context.Context
	logger              zerolog.Logger
	ID                  string
	Log                 string
	Config              string
	ip                  string
	commonErrorPatterns []string
}

func NewContainer(id, dir, ip string) *Container {
	logs := filepath.Join(dir, "logs")
	config := filepath.Join(dir, "config")
	cli, err := client.NewClientWithOpts(client.FromEnv)
	if err != nil {
		panic(err)
	}
	executionLog, err := os.Create(filepath.Join(logs, "execution.log"))
	if err != nil {
		panic(err)
	}
	output := zerolog.ConsoleWriter{Out: executionLog, TimeFormat: time.RFC3339}
	output.FormatLevel = func(i interface{}) string {
		return strings.ToUpper(fmt.Sprintf("| %-6s|", i))
	}
	output.FormatMessage = func(i interface{}) string {
		return fmt.Sprintf("***\n%s****", i)
	}
	output.FormatFieldName = func(i interface{}) string {
		return fmt.Sprintf("%s:", i)
	}
	output.FormatFieldValue = func(i interface{}) string {
		return strings.ToUpper(fmt.Sprintf("%s", i))
	}
	logger := zerolog.New(output).With().Timestamp().Logger()
	_, err = os.Create(filepath.Join(logs, "query.log"))
	if err != nil {
		panic(err)
	}
	_, err = os.Create(filepath.Join(logs, "trace.txt"))
	if err != nil {
		panic(err)
	}
	return &Container{
		client: cli,
		ctx:    context.Background(),
		logger: logger,
		ID:     id,
		Log:    logs,
		Config: config,
		ip:     ip,
		commonErrorPatterns: []string{
			"error:",
			"rndc: connect failed:",
		},
	}
}

type ExecResult struct {
	StdOut   string
	StdErr   string
	ExitCode int
}

func (c *Container) Exec(cmd []string) (ExecResult, error) {
	execConfig := types.ExecConfig{
		AttachStdout: true,
		AttachStderr: true,
		Cmd:          cmd,
	}
	var execResp ExecResult
	var err error
	timeout := 0 * time.Second
	numRetries := 10
	ok := true
	for ok && numRetries > 0 {
		time.Sleep(timeout)
		execResp, err = c.exec(execConfig)
		if err != nil {
			return execResp, err
		}
		numRetries -= 1
		timeout += 1 * time.Second
		ok = c.matchesError(execResp.StdErr)
	}
	return execResp, nil
}

func (c *Container) exec(execConfig types.ExecConfig) (ExecResult, error) {
	createResp, err := c.client.ContainerExecCreate(c.ctx, c.ID, execConfig)
	if err != nil {
		return ExecResult{}, err
	}
	execResp, err := c.inspectExecResp(createResp.ID)
	c.logger.Info().
		Str("containerID", c.ID).
		Msg(fmt.Sprintf("stdout: %s\nstderr: %s", execResp.StdOut, execResp.StdErr))
	if err != nil {
		return ExecResult{}, err
	}
	return execResp, nil
}

func (c *Container) matchesError(response string) bool {
	matched := false
	var err error
	for _, pattern := range c.commonErrorPatterns {
		matched, err = regexp.MatchString(pattern, response)
		if err != nil {
			panic(err)
		}
		if matched {
			return true
		}
	}
	return false
}

func (c *Container) inspectExecResp(execID string) (ExecResult, error) {
	attachResp, err := c.client.ContainerExecAttach(c.ctx, execID, types.ExecStartCheck{})
	if err != nil {
		return ExecResult{}, err
	}
	defer attachResp.Close()
	var outBuf, errBuf bytes.Buffer
	outputDone := make(chan error)

	go func() {
		_, err = stdcopy.StdCopy(&outBuf, &errBuf, attachResp.Reader)
		outputDone <- err
	}()
	select {
	case err := <-outputDone:
		if err != nil {
			return ExecResult{}, err
		}
		break
	case <-c.ctx.Done():
		return ExecResult{}, c.ctx.Err()
	}
	stdout, err := io.ReadAll(&outBuf)
	if err != nil {
		return ExecResult{}, err
	}
	stderr, err := io.ReadAll(&errBuf)
	if err != nil {
		return ExecResult{}, err
	}
	res, err := c.client.ContainerExecInspect(c.ctx, execID)
	if err != nil {
		return ExecResult{}, err
	}
	return ExecResult{
		ExitCode: res.ExitCode,
		StdOut:   string(stdout),
		StdErr:   string(stderr),
	}, nil
}

func (c *Container) ReadQueryLog(minTimeout time.Duration) []byte {
	var lines []string
	numberOfCurrentLines := 0
	for true {
		time.Sleep(minTimeout + time.Millisecond*100)
		queryLog, err := os.ReadFile(filepath.Join(c.Log, "query.log"))
		queryLog = bytes.ReplaceAll(queryLog, []byte{'\x00'}, []byte{})
		if err != nil {
			panic(err)
		}
		lines = strings.Split(string(queryLog), "\n")
		if len(lines) == numberOfCurrentLines {
			break
		}
		numberOfCurrentLines = len(lines)
	}
	return []byte(strings.Join(lines, "\n"))
}

func (c *Container) FlushQueryLog() {
	_, err := os.Create(filepath.Join(c.Log, "query.log"))
	if err != nil {
		panic(err)
	}
}
