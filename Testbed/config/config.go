package config

import (
	"fmt"
	"github.com/spf13/viper"
	"os"
	"path/filepath"
)

type Config struct {
	v    *viper.Viper
	path string
}

func New() *Config {
	path := "config"
	v := viper.New()
	v.AddConfigPath(path)
	v.SetDefault("Build", "build")
	v.SetDefault("Templates", filepath.Join("testbed", "templates"))
	v.SetDefault("QMin", false)
	return &Config{
		v:    v,
		path: path,
	}
}

func (c *Config) SetConfig(path, name string) error {
	configSrc, err := os.ReadFile(path)
	if err != nil {
		return err
	}
	if err := os.WriteFile(filepath.Join(c.path, fmt.Sprintf("%s.yaml", name)), configSrc, 0777); err != nil {
		return err
	}
	return nil
}

func (c *Config) Load(key string) interface{} {
	return c.v.Get(key)
}
