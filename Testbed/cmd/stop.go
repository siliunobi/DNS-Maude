package cmd

import (
	"github.com/spf13/cobra"
	"testbed/config"
	"testbed/testbed"
)

var cmdStop = &cobra.Command{
	Use:     "stop",
	Short:   "Stop the dns testbed",
	Example: "testbed stop",
	Args:    cobra.NoArgs,
	RunE: func(cmd *cobra.Command, args []string) error {
		testbedConfig, err := config.New().LoadTestbedConfig()
		if err != nil {
			return err
		}
		testbed.New(testbedConfig).Stop()
		return nil
	},
}
