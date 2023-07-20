package cmd

import (
	"fmt"
	"github.com/spf13/cobra"
	"os"
	"testbed/config"
	"testbed/testbed"
)

var cmdInit = &cobra.Command{
	Use:     "init [testbed config]",
	Short:   "Initialize a dns testbed",
	Example: "testbed init validation/testbed-basic.yaml",
	Args:    cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		_, err := initTestbed(args[0])
		return err
	},
}

func initTestbed(testbedConfigFile string) (*testbed.Testbed, error) {
	c := config.New()
	build := c.Load("build").(string)
	if _, err := os.Stat(build); !os.IsNotExist(err) {
		(&testbed.Testbed{Build: build}).Remove()
	}
	err := c.SetConfig(testbedConfigFile, "testbed")
	if err != nil {
		return nil, err
	}
	testbedConfig, err := c.LoadTestbedConfig()
	if err != nil {
		return nil, err
	}
	testbed.Build(testbedConfig)
	fmt.Println("### Initialized testbed ###")
	fmt.Println(testbed.New(testbedConfig))
	return testbed.New(testbedConfig), nil
}
