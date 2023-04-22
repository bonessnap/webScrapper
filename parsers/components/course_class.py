class Course:
    def __init__(self):
        self.Title = None
        self.Link = ""
        self.Author = ""
        self.Description = ""
        self.Tags = []
        self.ImageLink = ""
        self.Duration = ""
        self.Rate = 0
        self.RateCount = 0
        self.Students = 0
        self.Document = ""
        self.Language = ""
        self.Price = ""
        self.Difficulty = ""

    def __eq__(self, other):
        self.Tags.extend(other.Tags)
        set(self.Tags)
        return self.Link == other.Link

    def __hash__(self):
        return hash(self.Link)
    
    def printSelf(self):
        print("Title:", self.Title)
        print("Link:", self.Link)
        print("Author:", self.Author)
        #print("Desc:", len(self.Description), "symbols")
        print("Desc:", self.Description)
        print("Tags:", self.Tags)
        print("ImageLink:", self.ImageLink)
        print("Duration:", self.Duration)
        print("Rate:", self.Rate)
        print("Rates:", self.RateCount)
        print("Students:", self.Students)
        print("Document:", self.Document)
        print("Price:", self.Price)
        print("Difficulty:", self.Difficulty)


def getCourse():
    return Course()