package cmd

import (
	"github.com/spf13/cobra"
	"strconv"
	"testbed/config"
	"testbed/testbed"
	"time"
)

var cmdDelay = &cobra.Command{
	Use:     "delay [nameserver, duration (ms)]",
	Short:   "Delay the responses of a nameserver by the specified duration (in ms)",
	Example: "testbed delay target-com 800 ",
	Args:    cobra.ExactArgs(2),
	RunE: func(cmd *cobra.Command, args []string) error {
		testbedConfig, err := config.New().LoadTestbedConfig()
		if err != nil {
			return err
		}
		nameserver, err := testbed.New(testbedConfig).FindNameserver(args[0])
		if err != nil {
			return err
		}
		duration, err := strconv.ParseInt(args[1], 10, 64)
		if err != nil {
			return err
		}
		nameserver.SetDelay(time.Duration(duration) * time.Millisecond)
		return nil
	},
}
