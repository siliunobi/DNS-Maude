package cmd

import (
	"github.com/spf13/cobra"
	"testbed/config"
	"testbed/testbed"
)

var cmdStart = &cobra.Command{
	Use:     "start",
	Short:   "Build and run the dns testbed",
	Example: "testbed start",
	Args:    cobra.NoArgs,
	RunE: func(cmd *cobra.Command, args []string) error {
		testbedConfig, err := config.New().LoadTestbedConfig()
		if err != nil {
			return err
		}
		testbed.New(testbedConfig).Start()
		return nil
	},
}
