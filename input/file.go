package input

import (
	"os"

	"github.com/elastic/libbeat/logp"
)

type FileEvent struct {
	Source *string
	Offset int64
	Line   uint64
	Text   *string
	Fields *map[string]string

	Fileinfo *os.FileInfo
}

type File struct {
	File      *os.File
	FileInfo  os.FileInfo
	Path      string
	FileState *FileState
}

type Filer interface {
	GetState() *FileState
	IsSame()
	IsSameFile()
	IsRenamed()
}

// Builds and returns the FileState object based on the Event info.
func (f *FileEvent) GetState() *FileState {

	ino, dev := fileIds(f.Fileinfo)
	state := &FileState{
		Source: f.Source,
		// take the offset + length of the line + newline char and
		// save it as the new starting offset.
		// This issues a problem, if the EOL is a CRLF! Then on start it read the LF again and generates a event with an empty line
		Offset: f.Offset + int64(len(*f.Text)) + 1, // REVU: this is begging for BUGs
		Inode:  ino,
		Device: dev,
	}

	return state
}

// Check that the file isn't a symlink, mode is regular or file is nil
func (f *File) IsRegularFile() bool {
	if f.File == nil {
		logp.Critical("Harvester: BUG: f arg is nil")
		return false
	}

	info, e := f.File.Stat()
	if e != nil {
		logp.Err("File check fault: stat error: %s", e.Error())
		return false
	}

	if !info.Mode().IsRegular() {
		logp.Warn("Harvester: not a regular file: %q %s", info.Mode(), info.Name())
		return false
	}
	return true
}
